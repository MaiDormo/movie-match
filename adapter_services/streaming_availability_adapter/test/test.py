import unittest
import sys
import os

# Add the directory containing app.py to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class StreamingAvailabilityAdapterTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('STREAMING AVAILABILITY API Adapter is up and running!', response.get_data(as_text=True))

    def test_get_movie_availability_no_title(self):
        response = self.app.get('/api/v1/avail?country=us')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Movie title is required', response.get_data(as_text=True))

    def test_get_movie_availability_no_country(self):
        response = self.app.get('/api/v1/avail?title=Inception')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Country is required', response.get_data(as_text=True))

    def test_get_movie_availability_with_title_and_country(self):
        response = self.app.get('/api/v1/avail?title=Inception&country=us')
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.get_data(as_text=True))
        self.assertIn('success', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()