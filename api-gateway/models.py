from typing import Optional
from pydantic import BaseModel


class Genre(BaseModel):
    id: int
    name: str


class Movie(BaseModel):
    id: int
    title: str
    genres: list[Genre] | None = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    original_language: str
    original_title: str
    overview: Optional[str] = None
    popularity: float
    release_date: str
    runtime: int
    vote_average: float
    status: Optional[str] = None


class DiscoverResult(BaseModel):
    id: int
    title: str
    backdrop_path: Optional[str] = None
    genre_ids: list[int]
    popularity: float
    poster_path: Optional[str] = None
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
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    popularity: float
    overview: Optional[str] = None
    release_date: Optional[str] = None
    status: Optional[str] = None


class MovieRecommendations(BaseModel):
    movies: list[MovieRecommended]


class VibeList(BaseModel):
    vibes: list[str]


class EnrichmentResponse(BaseModel):
    tmdb_id: int
    youtube: Optional[dict] = None
    spotify: Optional[dict] = None
    trivia: Optional[dict] = None
    streaming: Optional[dict] = None
