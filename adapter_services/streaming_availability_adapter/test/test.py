import unittest
import sys
import os
from fastapi.testclient import TestClient

# Add the directory containing app.py to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

client = TestClient(app)

class StreamingAvailabilityAdapterTestCase(unittest.TestCase):
    def test_health_check(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('STREAMING AVAILABILITY API Adapter is up and running!', response.json().get('message'))

    def test_get_movie_availability_no_title(self):
        response = client.get('/api/v1/avail?country=us')
        self.assertEqual(response.status_code, 422)
        self.assertIn('Validation error', response.json().get('message'))

    def test_get_movie_availability_no_country(self):
        response = client.get('/api/v1/avail?title=Inception')
        self.assertEqual(response.status_code, 422)
        self.assertIn('Validation error', response.json().get('message'))

    def test_get_movie_availability_with_title_and_country(self):
        response = client.get('/api/v1/avail?title=Inception&country=us')
        self.assertEqual(response.status_code, 200)
        self.assertIn('service_name', response.json()[0])
        self.assertIn('service_type', response.json()[0])
        self.assertIn('quality', response.json()[0])

if __name__ == '__main__':
    unittest.main()