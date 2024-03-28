from flask import Flask, request, jsonify
from minio import Minio
from minio.error import S3Error

app = Flask(__name__)

client = Minio(
    "localhost:9000",
    access_key="YOUR-ACCESSKEY",
    secret_key="YOUR-SECRETKEY",
    secure=False,
)

BUCKET_NAME = 'images'

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        create_bucket(client, BUCKET_NAME)
        try:
            store_object(client, BUCKET_NAME, file.filename, file)
            return jsonify({"success": "Image uploaded successfully"}), 200
        except Exception as err:
            return jsonify({"error": str(err)}), 500
    return jsonify({"error": "Unknown error"}), 500