import os
import unittest
from unittest.mock import patch, mock_open
import json
from PIL import Image
import numpy as np
from io import BytesIO

from prediction_pipeline.embedding_service.app import app, extract_embeddings

class TestEmbeddingService(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_generate_embedding(self):
        # To test with a valid image file
        with open('tests/test_image.jpg', 'rb') as f:
            data = dict(image=(f, 'test_image.jpg'))
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
        with open('tests/test_file.txt', 'rb') as f:
            data = dict(image=(f, 'test_file.txt'))
            response = self.app.post('/generate_embedding', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertEqual(data['error'], 'Invalid file type')


