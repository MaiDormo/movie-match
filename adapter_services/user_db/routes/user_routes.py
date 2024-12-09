from flask import Blueprint
from controllers.user_controller import get_users, add_user

user_bp = Blueprint('user_bp', __name__)

user_bp.route('/users', methods=['GET'])(get_users)
user_bp.route('/users', methods=['POST'])(add_user)