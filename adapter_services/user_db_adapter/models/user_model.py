import uuid
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class MovieGenre(str, Enum):
    ACTION = "action"
    COMEDY = "comedy"
    DRAMA = "drama"
    HORROR = "horror"
    SCIFI = "sci-fi"
    #TODO! add more

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: str = Field(...)
    surname: str = Field(...)
    email: str = Field(..., description="Must be a valid email address")
    preferences: List[MovieGenre] = Field(..., description="List of preferred movie genres")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "name": "John",
                "surname": "Doe",
                "email": "john.doe@example.com",
                "preferences": ["action", "comedy"],
                "password": "securepassword123"
            }
        }

class UserUpdate(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    preferences: Optional[List[str]]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John",
                "surname": "Doe",
                "preferences": ["action", "fantasy"]
            }
        }