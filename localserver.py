from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import logging

app = Flask(__name__)
CORS(app)  # Esto permite solicitudes de cualquier origen

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/process_video', methods=['POST'])
def process_video():
    app.logger.info("Recibida solicitud POST a /process_video")
    app.logger.debug(f"Headers recibidos: {request.headers}")
    app.logger.debug(f"Datos recibidos: {request.get_data(as_text=True)}")

    try:
        data = request.json
        app.logger.info(f"Datos JSON parseados: {data}")
    except Exception as e:
        app.logger.error(f"Error al parsear JSON: {str(e)}")
        return jsonify({"error": "Invalid JSON data"}), 400

    video_url = data.get('video_url')
    row_id = data.get('row_id')
    
    if not video_url or not row_id:
        app.logger.warning("Falta video_url o row_id en la solicitud")
        return jsonify({"error": "Missing video_url or row_id"}), 400
    
    # Ejecuta tu script de Python
    try:
        app.logger.info(f"Intentando ejecutar: python videoanalyzer.py {video_url} {row_id}")
        subprocess.run(["python", "videoanalyzer.py", video_url, row_id], check=True)
        app.logger.info("Proceso iniciado con éxito")
        return jsonify({"message": "Process started successfully"}), 200
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error al ejecutar el subprocess: {str(e)}")
        return jsonify({"error": f"Error processing video: {str(e)}"}), 500
    except Exception as e:
        app.logger.error(f"Error inesperado: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)