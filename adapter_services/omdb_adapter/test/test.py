import unittest
import sys
import os
from fastapi.testclient import TestClient

# Add the directory containing app.py to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

client = TestClient(app)

class OMDBAdapterTestCase(unittest.TestCase):
    def test_health_check(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('OMDB API Adapter is up and running!', response.json().get('message'))

    def test_get_movies_no_title(self):
        response = client.get('/api/v1/search')
        self.assertEqual(response.status_code, 422)
        self.assertIn('Validation error', response.json().get('message'))

    def test_get_movies_with_title(self):
        response = client.get('/api/v1/search?title=Inception')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Title', response.json())

    def test_get_movie_id_no_id(self):
        response = client.get('/api/v1/find')
        self.assertEqual(response.status_code, 422)
        self.assertIn('Validation error', response.json().get('message'))

    def test_get_movie_id_with_id(self):
        response = client.get('/api/v1/find?id=tt1375666')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Title', response.json())

if __name__ == '__main__':
    unittest.main()