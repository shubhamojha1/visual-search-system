from flask import Flask, request, jsonify
from bucket_management import create_bucket
from object_storage import store_object, retrieve_object
from minio import Minio
import base64
import requests
import os
import logging
from werkzeug.utils import secure_filename
import tempfile


app = Flask(__name__)
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s') # make same changes in other API logging as well 

MINIO_HOST = os.environ.get('MINIO_HOST', 'localhost:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BASE_DIR = os.environ.get('MINIO_BASE_DIR', 'D:/visual-search-system/visual-search-system/common/storage') #'visual-search-system/common/storage')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB

EMBEDDING_GENERATION_SERVICE_URL = 'http://localhost:7000/generate_embedding'

client = Minio(
    MINIO_HOST,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)

# distributed MinIO cluster with replication factor of 3
data_dirs = [os.path.join(MINIO_BASE_DIR, "data1"),
             os.path.join(MINIO_BASE_DIR, "data2"),
              os.path.join(MINIO_BASE_DIR, "data3")]
# erasure_code_config = {"data": 2, "parity": 1}

# try:
#     client.set_erasure_code("myerasureset", data_dirs, erasure_code_config)
# except Exception as err:
#     logging.error(f"Error setting up MinIO cluster: {err}")


BUCKET_NAME = 'images'
try:
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME, erasure_code="myerasureset")
except Exception as err:
    logging.error(f"Error creating bucket: {err}")

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    print('file.filename ----> ', file.filename, type(file.filename))
    print('secure -----> ', secure_filename(file.filename), type(secure_filename(file.filename)))
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        if file.content_length > MAX_IMAGE_SIZE:
            return jsonify({'error': f'Image size exceeds the limit of {MAX_IMAGE_SIZE / (1024 * 1024)} MB'}), 413
        try:
            # Save image to MinIO
            # filename = secure_filename(file.filename)
            # object_name = f"{BUCKET_NAME}/{filename}"
            object_name = file.filename
            print("type checking ----> ",type(object_name), object_name)
            # result = client.fput_object(BUCKET_NAME, object_name, file_) # DOESNT WORK FOR SOME REASON
            # result = client.put_object(BUCKET_NAME, object_name, file.stream, file.content_length, file.content_type)
            store_object(client, BUCKET_NAME, file.filename, file.read())#file)

            # with tempfile.NamedTemporaryFile(delete=False) as tmp_file: # not scalable using tempfile
            embedding = generate_embedding(object_name, file) # NEED TO DO THIS IN indexing_service.

            save_embedding(object_name, embedding)

            # return jsonify({'success': 'Image uploaded and embedding generated successfully', 'embedding': embedding, 'object_name': result.object_name}), 200
            return jsonify({'success': 'Image uploaded and embedding generated successfully', 'embedding': embedding}), 200
        except Exception as err:
            logging.error(f"Error uploading or processing image: {err}")
            return jsonify({'error', 'Failed to upload or process the image'}), 500 # Break exception into multiple to deal with exact issue 
    else:
        return jsonify({'error': 'Invalid file type'}), 415
        
    
    # if file:
    #     create_bucket(client, BUCKET_NAME)
    #     print("file: ", file)
    #     try:
    #         file_content = file.read() # 
    #         # print(file_content)
    #         # print(file.filename)
    #         store_object(client, BUCKET_NAME, file.filename, file_content)#file)

    #         image_data = base64.b64encode(file_content).decode('utf-8')
    #         response = requests.post(EMBEDDING_GENERATION_SERVICE_URL, 
    #                                  files={
    #                                      'image': (file.filename, file.stream, file.content_type) # do not send 'file' object alone. WORKS THIS WAY ONLY
    #                                                                                                 # need to send other metadata as well. 
    #                                  })
    #         print(response)
    #         print(response.json())
    #         if response.status_code == 200:
    #             embedding = response.json()
    #             # save embedding to index table
    #             print(embedding)
    #             return jsonify({"success": "Image uploaded and embedding generated successfully", "embedding": embedding}), 200 
    #         else:
    #             return jsonify({"error": "Failed to generate embedding"}), 500
    #         # return jsonify({"success": "Image uploaded successfully"}), 200
    #     except Exception as err:
    #         return jsonify({"error": str(err)}), 500
    # return jsonify({"error": "Unknown error"}), 500

@app.route('/retrieve/<image_name>', methods=['GET'])
def retrieve_image(image_name):
    # try:
    #     response = retrieve_object(client, BUCKET_NAME, image_name)
    #     if response is None:
    #         return jsonify({"error": "Failed to retrieve image"}), 500
    #     return response
    # except Exception as err:
    #     return jsonify({"error": str(err)}), 500
    try:
        # object_name = f"{BUCKET_NAME}/{secure_filename(image_name)}" # original way
        object_name = image_name # temporarily
        # data = client.get_object(BUCKET_NAME, object_name).data
        print("object_name -----------> ", object_name)
        print("type checking ----> ",type(secure_filename(image_name)))
        response = retrieve_object(client, BUCKET_NAME, object_name) #client.get_object(BUCKET_NAME, object_name)
        print(response.status, response.headers, response.data)
        # data = b''
        data = response.data
        image_data = base64.b64encode(data).decode('utf-8')

        print("image_data -----------------------------> ", data)

        # Retrieve embedding from index table
        embedding = retrieve_embedding(object_name)
        return jsonify({'image': image_data, 'embedding': embedding})
    except Exception as err:
        logging.error(f"Error retrieving image: {err}")
        return jsonify({'error': 'Failed to retrieve image'}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_embedding(object_name, file):
    try:
        response = requests.post(EMBEDDING_GENERATION_SERVICE_URL, 
                                     files={
                                         'image': (file.filename, file.stream, file.content_type) # do not send 'file' object alone. WORKS THIS WAY ONLY
                                                                                                    # need to send other metadata as well. 
                                     })
        if response.status_code == 200:
            return response.json()['embedding']
        else:
            logging.error(f"Error generating embedding: {response.text}")
            raise Exception("Failed to generate image embedding")
    except Exception as err:
        logging.error(f"Error generating embedding: {err}")
        raise err
    
def save_embedding(object_name, embedding):
    # Save embedding to the index table/db
    pass

def retrieve_embedding(object_name):
    # Retrieve embedding from index table/ db
    return {'embedding': [0.1, 0.2, 0.3, 0.4, 0.5]} # placeholder value


    
if __name__ == '__main__':
    app.run(debug=True, port=8889)