from pydantic import BaseModel


class Genres(BaseModel):
    id: int
    name: str

class TMDBMovie(BaseModel):
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
    status: str

class TMDBDiscoverResult(BaseModel):
    id: int
    title: str
    backdrop_path: str
    genre_ids: list[int]
    popularity: float
    poster_path: str
    release_date: str
    vote_average: float

class TMDBDiscoverResponse(BaseModel):
    page: int
    results: list[TMDBDiscoverResult]
    total_pages: int
    total_results: int

