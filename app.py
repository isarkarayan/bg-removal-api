from flask import Flask, request, jsonify, send_file
import os
API_KEY = os.getenv('API_KEY', str(uuid.uuid4()))
import uuid
from werkzeug.utils import secure_filename
from bg_removal import process_image

app = Flask(__name__)

# Generate a unique API key
API_KEY = str(uuid.uuid4())
print(f"Generated API Key: {API_KEY}")

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Middleware to check API key
def check_api_key():
    provided_key = request.headers.get('X-API-Key')
    if provided_key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    auth_error = check_api_key()
    if auth_error:
        return auth_error

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"processed_{filename}")

    file.save(input_path)
    process_image(input_path, output_path)

    return send_file(output_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)