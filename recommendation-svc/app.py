from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from config import engine, get_db_session
from models import Base, Movie, MovieRecommendations, MovieRecommended


# recommendation-svc/vibes.py

VIBE_MAP = {
    # ---------- core moods ----------
    "chill": [18, 10751, 10402, 99],          # Drama, Family, Music, Documentary → relaxed, thoughtful
    "dark": [27, 53, 9648, 80],               # Horror, Thriller, Mystery, Crime → gritty, tense
    "funny": [35, 10751, 10770],              # Comedy, Family, TV Movie → laughs
    "romantic": [10749, 18, 35],              # Romance, Drama, Comedy → love stories (dramatic or funny)
    "action-packed": [28, 12, 53],            # Action, Adventure, Thriller → adrenaline rush
    "feel-good": [35, 18, 10751, 10402],      # Comedy, Drama, Family, Music → uplifting
    "mind-bending": [878, 9648, 53, 12],      # Sci-Fi, Mystery, Thriller, Adventure → twists & speculation
    "heartwarming": [18, 10751, 36, 10749],   # Drama, Family, History, Romance → emotional, earnest
    "spooky": [27, 53, 9648, 878],            # Horror, Thriller, Mystery, Sci-Fi → eerie atmospheres
    "epic": [12, 14, 28, 36],                 # Adventure, Fantasy, Action, History → grand scale
    "gritty": [80, 18, 53, 28],               # Crime, Drama, Thriller, Action → raw & uncompromising
    "magical": [14, 12, 10751, 878],          # Fantasy, Adventure, Family, Sci-Fi → wonderment
    "nerdy": [878, 28, 16, 9648],             # Sci-Fi, Action, Animation, Mystery → geek culture staples
    "laugh-out-loud": [35],                    # pure Comedy
    "tearjerker": [18, 10749],                # Drama + Romance (sad stories)
    "thrill-ride": [28, 53, 12, 9648],        # Action, Thriller, Adventure, Mystery → non-stop excitement
    "wholesome": [10751, 16, 99, 10402],      # Family, Animation, Documentary, Music → clean enjoyment
    "rebellious": [28, 80, 35, 10402],        # Action, Crime, Comedy, Music → anti-establishment
    "futuristic": [878, 28, 12, 53],          # Sci-Fi, Action, Adventure, Thriller → cutting-edge tech
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title = "Recommendation Service", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok", "messagge": "Recommendation Service is up and running!"}


# Example endpoint that uses the database (placeholder)
@app.get("/db-check")
async def db_check(db: AsyncSession = Depends(get_db_session)):
    # Just a simple query to verify the database connection works
    result = await db.execute(text("SELECT 1"))
    return {"db": "connected", "data": result.scalar()}

# Input: list of genres -> str
@app.get("/v1/recommend/by-genres", response_model=MovieRecommendations)
async def reccomend_by_genre(genres: str = Query(..., description="List of genres comma separated ','"), db: AsyncSession = Depends(get_db_session)):
    genres_ids = [int(genre) for genre in genres.split(",")]
    # define a query that is able to collect witch of these movies make sense to show
    stmt = text("""SELECT id, title, poster_path, backdrop_path, popularity, overview, release_date, status,
                    array_length(ARRAY(SELECT UNNEST(genre_ids) INTERSECT SELECT UNNEST(CAST(:genres AS int[]))), 1) AS match_count
                FROM movies
                WHERE genre_ids && CAST(:genres AS int[])
                ORDER BY match_count DESC, popularity DESC
                LIMIT 20
    """)
    result =  await db.execute(stmt, params={"genres": genres_ids})
    rows = result.mappings().all()
    recommended_movies = [MovieRecommended(**row) for row in rows]
    return MovieRecommendations(movies=recommended_movies)


# Input: Movie id -> str
@app.get("/v1/recommend/similar", response_model=MovieRecommendations)
async def recommend_similar(id: int = Query(..., description="movie id")):
    # define a query that return the score similar to 
    pass


@app.get("/v1/recommend/by-vibe", response_model=MovieRecommendations)
async def recommend_by_vibe(
        vibes: str = Query(..., description="Comma-separated vibe names"),
        db: AsyncSession = Depends(get_db_session)
):
    vibe_list = [v.strip().lower() for v in vibes.split(",")]
    genre_set = set()
    
    for v in vibe_list:
        genre_set.update(VIBE_MAP.get(v,[]))

    if not genre_set:
        raise HTTPException(status_code=400, detail="No valid vibes provided")
    genre_ids = list(genre_set)
    stmt = text("""SELECT id, title, poster_path, backdrop_path, popularity, overview, release_date, status,
                    array_length(ARRAY(SELECT UNNEST(genre_ids) INTERSECT SELECT UNNEST(CAST(:genres AS int[]))), 1) AS match_count
                FROM movies
                WHERE genre_ids && CAST(:genres AS int[])
                ORDER BY match_count DESC, popularity DESC
                LIMIT 20
    """)
    result =  await db.execute(stmt, params={"genres": genre_ids})
    rows = result.mappings().all()
    recommended_movies = [MovieRecommended(**row) for row in rows]
    return MovieRecommendations(movies=recommended_movies)



