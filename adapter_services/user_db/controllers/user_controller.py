from flask import jsonify, request
from models.user_model import users

def get_users():
    try:
        all_users = list(users.find({}, {'_id': 0}))
        return jsonify(all_users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def add_user():
    try:
        user = request.json
        users.insert_one(user)
        return jsonify({'msg': 'User added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500