import os
import torch
from torchvision import transforms
from efficientnet_pytorch import EfficientNet
import faiss
from PIL import Image
import numpy as np
# from io import BytesIO
from werkzeug.utils import secure_filename
import imghdr
from flask import Flask, request, jsonify
import logging
from flask_caching import Cache
from typing import List

app = Flask(__name__)

BATCH_SIZE = 32

config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 3600
}

app.config.from_mapping(config)
cache = Cache(app)

# Configuring logging
logging.basicConfig(filename='app.log', level=logging.INFO)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp'}

model = EfficientNet.from_pretrained('efficientnet-b7')
model.eval() # setting to eval mode

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# index = faiss.IndexFlatL2(model.classifier.out_features)
index = faiss.IndexFlatL2(model._fc.in_features)
embeddings = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    # return True

def extract_embeddings(image):
    with torch.no_grad():
        input_tensor = preprocess(image).unsqueeze(0)
        embedding = model.extract_features(input_tensor).cpu().numpy().flatten()
    return embedding


# function for batching (processing multiple images simultaneously, will implement later)
# def extract_embeddings(images: List[Image.Image]) -> List[np.ndarray]:
#     input_tensors = []
#     for image in images:
#         input_tensor = preprocess(image).unsqueeze(0)
#         input_tensors.append(input_tensor)

#     input_batch = torch.cat(input_tensors)
#     with torch.no_grad():
#         embeddings = model.extract_features(input_batch).cpu().numpy()

#     return embeddings

@app.route('/generate_embedding', methods=['POST'])
def generate_embedding():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        cache_key = f'embedding_{image_file.filename}'
        print("image file ----> ",image_file)
        cached_embedding = cache.get(cache_key)
        if cached_embedding:
            return jsonify({'embedding': cached_embedding})

        if image_file.filename == '':
            return jsonify({'error': 'No image file provided'}), 400
        
        if not allowed_file(image_file.filename):
            print(image_file.filename)
            return jsonify({'error': 'Invalid file type'}), 400
        
        if imghdr.what(image_file) is None:
            return jsonify({'error': 'Invalid image file'}), 400
        # image_path = os.path.join('images', image.filename)
        # image = Image.open(image_file)
        # image.save(image_path)
        # image_bytes = image_file.read()
        # image_stream = BytesIO(image_bytes)
        # image_stream.seekable = True
        print("*"*100)
        print(image_file)
        logging.info(f'Generated embedding for image: {image_file.filename}')
        image = Image.open(image_file.stream)
    except Exception as e:
        logging.error(f'Error generating embedding: {str(e)}')
        return jsonify({'error': str(e)}), 500
    
    embedding = extract_embeddings(image)
    embedding_list = embedding.tolist()
    # embeddings.append(embedding)
    # index.add(np.array(embedding))
    cache.set(cache_key, embedding_list)
    
    return jsonify({'embedding':embedding_list})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)

