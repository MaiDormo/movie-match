from typing import Optional
from pydantic import BaseModel


class EnrichmentRequest(BaseModel):
    tmdb_id: int


class YouTubeResult(BaseModel):
    embed_url: Optional[str] = None
    video_id: Optional[str] = None
    title: Optional[str] = None


class SpotifyResult(BaseModel):
    spotify_url: Optional[str] = None
    cover_url: Optional[str] = None
    name: Optional[str] = None


class TriviaResult(BaseModel):
    question: Optional[str] = None
    options: Optional[list[str]] = None
    correct_answer: Optional[str] = None


class StreamingService(BaseModel):
    service_name: Optional[str] = None
    logo: Optional[str] = None
    link: Optional[str] = None


class StreamingResult(BaseModel):
    services: Optional[list[StreamingService]] = None


class EnrichmentResponse(BaseModel):
    tmdb_id: int
    title: Optional[str] = None
    imdb_id: Optional[str] = None
    poster_path: Optional[str] = None
    release_date: Optional[str] = None
    runtime: Optional[int] = None
    genres: Optional[list[dict]] = None
    overview: Optional[str] = None
    vote_average: Optional[float] = None
    youtube: Optional[YouTubeResult] = None
    spotify: Optional[SpotifyResult] = None
    trivia: Optional[TriviaResult] = None
    streaming: Optional[StreamingResult] = None
