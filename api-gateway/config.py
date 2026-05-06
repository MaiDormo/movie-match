from pydantic import BaseModel

class EndpointConfig(BaseModel):
    movieUrl: str = "http://movie-core:5000/v1/movie"
    discoverUrl: str = "http://movie-core:5000/v1/discover"
    vibeUrl: str = "http://recommendation-svc/v1/recommend/similar"
    similarUrl: str = "http://recommendation-svc/v1/recommend/by-vibe"
    posterUrl: str = "https://image.tmdb.org/t/p/original"


def get_endpoint_config() -> EndpointConfig:
    return EndpointConfig()



