from flask import Flask, request, jsonify
from bucket_management import create_bucket
from object_storage import store_object, retrieve_object
from minio import Minio


app = Flask(__name__)

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
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
        print(file)
        try:
            file_content = file.read() # 
            # print(file_content)
            # print(file.filename)
            store_object(client, BUCKET_NAME, file.filename, file_content)#file)
            return jsonify({"success": "Image uploaded successfully"}), 200
        except Exception as err:
            return jsonify({"error": str(err)}), 500
    return jsonify({"error": "Unknown error"}), 500

@app.route('/retrieve/<image_name>', methods=['GET'])
def retrieve_image(image_name):
    try:
        data = retrieve_object(client, BUCKET_NAME, image_name, "retrieved_image.jpg")
        return data, 200
    except Exception as err:
        return jsonify({"error": str(err)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)