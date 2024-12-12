from flask import Blueprint
from controllers.streaming_availability_controller import get_movie_availability, health_check

streaming_availability_bp = Blueprint("streaming_availability_bp", __name__)

streaming_availability_bp.route("/", methods=["GET"])(health_check)
streaming_availability_bp.route("/api/v1/avail", methods=["GET"])(get_movie_availability)
