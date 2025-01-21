import uuid
from typing import Optional, List, Union
from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: str = Field(...)
    surname: str = Field(...)
    email: str = Field(..., description="Must be a valid email address")
    preferences: List[int] = Field(..., description="List of preferred movie genres")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "name": "John",
                "surname": "Doe",
                "email": "john.doe@example.com",
                "preferences": [28, 35],
                "password": "securepassword123"
            }
        }

class UserUpdate(BaseModel):
    name: str | None = None
    surname: str | None = None
    preferences: list[int] | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "preferences": [28, 14]
            }
        }