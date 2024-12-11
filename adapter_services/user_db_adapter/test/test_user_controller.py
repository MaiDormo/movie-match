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
        response = self.app.post('/users', json={
            'username': 'john_doe',
            'email': 'john@example.com',
            'full_name': 'John Doe',
            'role': 'user',
            'hashed_password': 'hashed_password_example',
            'interests': ['programming', 'machine learning', 'python']
        })
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()