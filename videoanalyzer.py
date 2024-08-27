import os
import subprocess
import glob
import time
import google.generativeai as genai

# Configura tu API key
genai.configure(api_key="AIzaSyBfsVN0167n7r1DYAzJ3xpa2ygU3FksFQk")

def download_video(youtube_url):
    # Comando para descargar el video usando yt-dlp
    command = ["yt-dlp", "-o", "%(title)s.%(ext)s", youtube_url]
    subprocess.run(command)

def upload_and_analyze_video(file_path):
    # Subir el archivo
    video_file = genai.upload_file(file_path)
    print(f"Archivo subido: {video_file.uri}")

    # Esperar a que el archivo esté en estado ACTIVE
    while video_file.state.name == "PROCESSING":
        print('.', end='', flush=True)
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(f"Error al procesar el archivo: {video_file.state.name}")

    # Inicializa el modelo
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Prepara el prompt
    prompt = """
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

def main():
    # Solicitar la URL del video al usuario
    youtube_url = input("Introduce la URL del video de YouTube: ")
    
    # Descargar el video
    download_video(youtube_url)
    
    # Obtener el nombre del archivo descargado
    video_files = glob.glob("*.webm") + glob.glob("*.mp4")  # Busca archivos .webm y .mp4
    video_file = video_files[0] if video_files else None
    
    if video_file:
        try:
            # Analizar el video
            analysis = upload_and_analyze_video(video_file)
            
            # Mostrar el resultado
            print("\nAnálisis del video:")
            print(analysis)
        except Exception as e:
            print(f"Error al analizar el video: {str(e)}")
    else:
        print("No se encontró el archivo de video.")

if __name__ == "__main__":
    main()





