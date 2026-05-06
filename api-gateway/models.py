from pydantic import BaseModel


class Genres(BaseModel):
    id: int
    name: str

class Movie(BaseModel):
    id: int
    title: str
    genres: list[Genres] | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    original_language: str
    original_title: str
    overview: str | None = None
    popularity: float
    release_date: str
    runtime: int
    vote_average: float
    status: str | None = None


class DiscoverResult(BaseModel):
    id: int
    title: str
    backdrop_path: str
    genre_ids: list[int]
    popularity: float
    poster_path: str
    release_date: str
    vote_average: float

class DiscoverResponse(BaseModel):
    page: int
    results: list[DiscoverResult]
    total_pages: int
    total_results: int


class MovieRecommended(BaseModel):
    id: int
    title: str
    poster_path: str | None = None
    backdrop_path: str | None = None
    popularity: float
    overview: str | None = None
    release_date: str | None = None
    status: str | None = None

class MovieRecommendations(BaseModel):
    movies: list[MovieRecommended]
