from flask import Blueprint
from controllers.omdb_controller import get_movie_id, get_movies, health_check

omdb_bp = Blueprint('omdb_bp', __name__)

omdb_bp.route('/', methods=['GET'])(health_check)
omdb_bp.route('/api/v1/movies', methods=['GET'])(get_movies)
omdb_bp.route('/api/v1/movie', methods=['GET'])(get_movie_id)