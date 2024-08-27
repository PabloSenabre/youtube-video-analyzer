import os
import subprocess
import glob
import time
import logging
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests  # Añadido para las solicitudes a Coda

# Configuración de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()  # Carga las variables de entorno desde .env

app = Flask(__name__)
CORS(app)

# Configura tu API key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def download_video(youtube_url):
    # Comando para descargar el video usando yt-dlp
    command = ["yt-dlp", "-o", "%(title)s.%(ext)s", youtube_url]
    subprocess.run(command)

def upload_and_analyze_video(file_path, custom_prompt):
    try:
        # Subir el archivo
        video_file = genai.upload_file(file_path)
        logging.debug(f"Archivo subido: {video_file.uri}")

        # Esperar a que el archivo esté en estado ACTIVE
        while video_file.state.name == "PROCESSING":
            print('.', end='', flush=True)  # Cambiado de logging.debug a print
            time.sleep(10)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError(f"Error al procesar el archivo: {video_file.state.name}")

        # Inicializa el modelo
        model = genai.GenerativeModel('gemini-1.5-pro')

        # Usa el prompt personalizado si se proporciona, de lo contrario usa el predeterminado
        prompt = custom_prompt if custom_prompt else """
        <detailed_report>
        <overview>
        You are a highly perceptive AI assistant specialized in comprehensive video analysis. Your task is to examine the video provided and generate an in-depth, structured report. This report will serve as a foundation for other AI systems to understand and work with the video's content, so it's crucial to be as thorough and precise as possible.
        </overview>
        <instructions>
        Analyze the video and create a detailed report following these guidelines:

        Video Overview:
        Provide a comprehensive summary of the video's content, purpose, and main themes.
        Visual Analysis:

        Describe the visual elements in detail, including setting, characters, objects, and any text or graphics.
        Analyze the cinematography, including camera angles, movements, and shot compositions.
        Identify any visual effects or animations used.


        Audio Analysis:

        Describe the audio components, including dialogue, narration, music, and sound effects.
        Analyze the tone, mood, and emotional impact of the audio elements.


        Content Structure:

        Break down the video into its main sections or scenes.
        Identify the narrative structure or educational flow, if applicable.


        Key Components:
        Detail any specific elements that are central to the video's purpose, such as:
        a. Main characters or presenters
        b. Key concepts or topics covered
        c. Important visual aids or demonstrations
        d. Crucial information or data presented
        Technical Details:
        Include information about the video's technical aspects, such as quality, duration, and format.
        Purpose and Target Audience:
        Analyze the intended purpose of the video and its target audience.
        Context and Background:
        Provide any relevant context or background information that enhances understanding of the video's content.
        Key Takeaways:
        Summarize the main points, lessons, or messages conveyed in the video.
        Potential Applications:
        Suggest possible uses or scenarios where the information from this video could be applied.

        Organize your explanation using appropriate headings and subheadings. Use bullet points or numbered lists where applicable to improve readability. Explain any technical terms or concepts that may not be familiar to a general audience.
        Your report should be extremely detailed, aiming to capture and convey every significant aspect of the video. Imagine that the AI system reading your report has no prior knowledge of the video's content and needs to understand every nuance of its presentation and message.
        Begin your explanation with an introductory paragraph summarizing the video, then proceed with the detailed sections. Conclude with a summary of the key points and the potential impact or significance of the video's content.
        </instructions>
        Based on the video you have analyzed, please provide your comprehensive analysis:
        [Your detailed analysis goes here, following the structure and guidelines provided in the instructions.]
        </detailed_report>
        """

        # Genera el contenido
        response = model.generate_content([prompt, video_file],
                                          request_options={"timeout": 600})

        return response.text
    except Exception as e:
        logging.error(f"Error en upload_and_analyze_video: {str(e)}", exc_info=True)
        raise

def insert_to_coda(analysis, video_title):
    coda_api_token = os.getenv('CODA_API_TOKEN')
    doc_id = os.getenv('CODA_DOC_ID')
    table_id_or_name = os.getenv('CODA_TABLE_ID')
    
    headers = {
        "Authorization": f"Bearer {coda_api_token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://coda.io/apis/v1/docs/{doc_id}/tables/{table_id_or_name}/rows"
    
    payload = {
        "rows": [
            {
                "cells": [
                    {"column": "Video ID", "value": video_title},
                    {"column": "Analysis", "value": analysis}
                ]
            }
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 202:
        return True
    else:
        raise Exception(f"Error al insertar en Coda: {response.text}")

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    logging.debug(f"Received request: {request.method} {request.url}")
    logging.debug(f"Headers: {request.headers}")

    if request.method == 'OPTIONS':
        return '', 204

    logging.debug(f"Request data: {request.json}")

    data = request.json
    youtube_url = data.get('youtube_url')
    custom_prompt = data.get('custom_prompt')

    if not youtube_url:
        return jsonify({'error': 'No se proporcionó URL de YouTube'}), 400

    try:
        # Descargar el video
        download_video(youtube_url)

        # Obtener el nombre del archivo descargado
        video_files = glob.glob("*.webm") + glob.glob("*.mp4")  # Busca archivos .webm y .mp4
        video_file = video_files[0] if video_files else None

        if video_file:
            # Obtener el título del video (nombre del archivo sin extensión)
            video_title = os.path.splitext(video_file)[0]
            
            # Analizar el video
            analysis = upload_and_analyze_video(video_file, custom_prompt)
            
            # Insertar el análisis en Coda
            insert_to_coda(analysis, video_title)

            # Limpiar el archivo descargado
            os.remove(video_file)

            return jsonify({'analysis': analysis, 'coda_insert': 'success', 'video_title': video_title})
        else:
            return jsonify({'error': 'No se encontró el archivo de video'}), 500
    except Exception as e:
        logging.error(f"Error en /analyze: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)