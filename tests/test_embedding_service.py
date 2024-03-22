import os
import unittest
from unittest.mock import patch, mock_open
import json
from PIL import Image
import numpy as np
from io import BytesIO
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from prediction_pipeline.embedding_service import app, extract_embeddings

# print(os.getcwd())

class TestEmbeddingService(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_generate_embedding(self):
        # To test with a valid image file
        with open('test_image.jpeg', 'rb') as f:
            data = dict(image=(f, 'test_image.jpeg'))
            response = self.app.post('/generate_embedding', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIsInstance(data['embedding'], list)
            self.assertGreater(len(data['embedding']), 0)

        # To test with no image file provided
        response = self.app.post('/generate_embedding')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'No image file provided')

        # To test with invalid file type
        with open('test_file.txt', 'rb') as f:
            data = dict(image=(f, 'test_file.txt'))
            response = self.app.post('/generate_embedding', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertEqual(data['error'], 'Invalid file type')

    @patch('app.extract_embeddings')
    def test_extract_embedding(self, mock_extract_embedding):
        mock_image = mock_open(read_data=b'mock_image_data').return_value
        mock_extract_embedding.return_value = np.array([1.0, 2.0, 3.0])
        embedding = extract_embeddings(mock_image)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.tolist(), [1.0, 2.0, 3.0])

    def test_input_validation(self):
        with open('test_image.jpg', 'rb') as f:
            data = dict(image=(f, ''))
            response = self.app.post('/generate_embedding', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertEqual(data['error'], 'No image file provided')

        mock_image = mock_open(read_data=b'invalid_image_data').return_value
        with patch('PIL.Image.open', return_value=mock_image):
            with open('tests/test_image.jpg', 'rb') as f:
                data = dict(image=(f, 'test_image.jpeg'))
                response = self.app.post('/generate_embedding', data=data, content_type='multipart/form-data')
                self.assertEqual(response.status_code, 400)
                data = json.loads(response.data)
                self.assertEqual(data['error'], 'Invalid image file')

    def test_error_handling(self):
    # Test with an exception raised during embedding generation
        with patch('app.extract_embeddings', side_effect=Exception('Test exception')):
            with open('tests/test_image.jpg', 'rb') as f:
                data = dict(image=(f, 'test_image.jpg'))
                response = self.app.post('/generate_embedding', data=data, content_type='multipart/form-data')
                self.assertEqual(response.status_code, 500)
                data = json.loads(response.data)
                self.assertEqual(data['error'], 'Test exception')


if __name__ == "__main__":
    # print(os.getcwd())
    unittest.main()


