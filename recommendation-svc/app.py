from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from config import engine, get_db_session
from models import Base


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
    return {"db": "connected", "value": result.scalar()}
