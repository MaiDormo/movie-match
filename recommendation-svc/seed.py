# seed.py
import asyncio
import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models import Movie, Base  # your SQLAlchemy models
from config import engine, AsyncSessionLocal     # uses pydantic-settings for env vars


# Global genre list – you’d define this once
ALL_GENRES = [28, 12, 16, 35, 80, 99, 18, 10751, 14, 36, 27, 10402, 9648, 10749, 878, 10770, 53, 10752, 37]

def build_genre_vector(genre_ids: list[int]) -> list[int]:
    """Convert a list of genre IDs to a fixed-length binary vector."""
    return [1 if g in genre_ids else 0 for g in ALL_GENRES]

async def fetch_movies(client: httpx.AsyncClient, page: int = 1):
    """Fetch movies from movie-core's discover endpoint."""
    url = "http://movie-core:5000/api/v1/discover"
    params = {
        "language": "en-US",
        "with_genres": "",        # or fill with desired genres
        "page": page,
    }
    resp = await client.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data["results"]

async def seed():
    # 1. Ensure tables exist (use Alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Fetch movies from movie-core
    async with httpx.AsyncClient(timeout=30.0) as client:
        all_movies = []
        # For full seed, loop until total_pages; here just a few pages
        for page in range(1,11):
            batch = await fetch_movies(client, page)
            all_movies.extend(batch)

    # 3. Upsert into DB using your sessionmaker
    async with AsyncSessionLocal() as session:
        for movie_data in all_movies:
            genre_ids = movie_data.get("genre_ids", [])
            vector = build_genre_vector(genre_ids)
            stmt = text("""
                INSERT INTO movies (id, title, genre_ids, popularity, poster_path, genre_vector)
                VALUES (:id, :title, :genre_ids, :popularity, :poster_path, :vector)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    genre_ids = EXCLUDED.genre_ids,
                    popularity = EXCLUDED.popularity,
                    poster_path = EXCLUDED.poster_path,
                    genre_vector = EXCLUDED.genre_vector
            """)
            await session.execute(stmt, {
                "id": movie_data["id"],
                "title": movie_data["title"],
                "genre_ids": genre_ids,
                "popularity": movie_data.get("popularity"),
                "poster_path": movie_data.get("poster_path"),
                "vector": vector,
            })
        await session.commit()
    print(f"Seeded {len(all_movies)} movies successfully.")

if __name__ == "__main__":
    asyncio.run(seed())
