import os
import torch
from torchvision import transforms
from efficientnet_pytorch import EfficientNet
import faiss
from PIL import Image
import numpy as np
from io import BytesIO
from flask import Flask, request, jsonify

app = Flask(__name__)

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

def extract_embeddings(image):
    with torch.no_grad():
        input_tensor = preprocess(image).unsqueeze(0)
        embedding = model.extract_features(input_tensor).cpu().numpy().flatten()
    return embedding

@app.route('/generate_embedding', methods=['POST'])
def generate_embedding():
    image_file = request.files['image']
    # image_path = os.path.join('images', image.filename)
    # image = Image.open(image_file)
    # image.save(image_path)
    # image_bytes = image_file.read()
    # image_stream = BytesIO(image_bytes)
    # image_stream.seekable = True
    image = Image.open(image_file.stream)

    embedding = extract_embeddings(image)
    # embeddings.append(embedding)
    # index.add(np.array(embedding))
    
    return jsonify({'embedding':embedding.tolist()})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

