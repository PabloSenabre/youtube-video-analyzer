from flask import Flask, request, send_file, jsonify
from pytube import YouTube
import os
import tempfile

app = Flask(__name__)

@app.route('/api/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        
        # Crear un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_filename = temp_file.name
        
        # Descargar el video
        stream.download(output_path=os.path.dirname(temp_filename), filename=os.path.basename(temp_filename))
        
        # Enviar el archivo
        return send_file(temp_filename, as_attachment=True, download_name=f"{yt.title}.mp4")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Eliminar el archivo temporal
        if 'temp_filename' in locals():
            os.remove(temp_filename)

@app.route('/')
def home():
    return "YouTube Downloader API is running!"

if __name__ == '__main__':
    app.run(debug=True)