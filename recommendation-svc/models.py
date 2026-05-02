from sqlalchemy import Column, Float, Integer, String, ARRAY
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    genre_ids = Column(ARRAY(Integer), nullable=False)
    genre_vector = Column(ARRAY(Integer), nullable=False)
    popularity = Column(Float)
    poster_path = Column(String)
    backdrop_path = Column(String)
    original_language = Column(String)
    original_title = Column(String)
    overview = Column(String)
    release_date = Column(String)
    status = Column(String)
