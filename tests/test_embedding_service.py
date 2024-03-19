import os
import unittest
from unittest.mock import patch, mock_open
import json
from PIL import Image
import numpy as np
from io import BytesIO

from prediction_pipeline.embedding_service.app import app, extract_embeddings

class TestEmbeddingService(unittest.TestCase):
    pass
