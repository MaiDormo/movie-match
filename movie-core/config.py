import os
from pydantic import BaseModel

# TODO Add poster URL

class TMDBConfig(BaseModel):
    tmdbMovieDetails: str = "https://api.themoviedb.org/3/movie/"
    tmdbMovieDiscover: str = "https://api.themoviedb.org/3/discover/movie"
    tmdbKey: str | None = os.getenv("TMDB_API_KEY")

def getTMDBConfig() -> TMDBConfig:
    return TMDBConfig()




