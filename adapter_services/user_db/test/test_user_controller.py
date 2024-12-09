import unittest
from app import app

class UserControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_users(self):
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)

    def test_add_user(self):
        response = self.app.post('/users', json={'name': 'John', 'age': 25})
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()