import unittest
import sys
import os

# Add the directory containing app.py to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class OMDBAdapterTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('OMDB API Adapter is up and running!', response.get_data(as_text=True))

    def test_get_movies_no_title(self):
        response = self.app.get('/api/v1/movies')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Movie title is required', response.get_data(as_text=True))

    def test_get_movies_with_title(self):
        response = self.app.get('/api/v1/movies?t=Inception')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Title', response.get_data(as_text=True))

    def test_get_movie_id_no_id(self):
        response = self.app.get('/api/v1/movie')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Movie ID is required', response.get_data(as_text=True))

    def test_get_movie_id_with_id(self):
        response = self.app.get('/api/v1/movie?i=tt1375666')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Title', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()