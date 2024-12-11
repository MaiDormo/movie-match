from flask import jsonify, request
from models.user_model import users, UserModel

def get_users():
    try:
        all_users = list(users.find({}, {'_id': 0}))
        return jsonify(all_users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def add_user():
    try:
        user_data = request.json
        user = UserModel(**user_data)
        users.insert_one(user.model_dump(by_alias=True))
        return jsonify({'msg': 'User added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500