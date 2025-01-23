import uuid
from typing import List
from pydantic import BaseModel, Field

class User(BaseModel):
    """
    Represents a user in the system.
    
    This model is used for creating and retrieving user information.
    The _id field is auto-generated using UUID4.
    """
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        alias="_id",
        description="Unique identifier for the user (auto-generated UUID4)",
        example="066de609-b04a-4b30-b46c-32537c7f1f6e"
    )
    name: str = Field(
        ...,
        description="User's first name",
        min_length=1,
        max_length=50,
        example="John"
    )
    surname: str = Field(
        ...,
        description="User's last name",
        min_length=1,
        max_length=50,
        example="Doe"
    )
    email: str = Field(
        ...,
        description="User's email address - must be a valid email format",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        example="john.doe@example.com"
    )
    preferences: List[int] = Field(
        ...,
        description="List of genre IDs representing user's movie preferences",
        min_items=0,
        max_items=20,
        example=[28, 35]
    )
    password: str = Field(
        ...,
        description="User's password - must be at least 8 characters long",
        min_length=8,
        max_length=100,
        example="securepassword123"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "description": "User model for registration and profile management",
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
    """
    Represents a user update request.
    
    This model is used for updating existing user information.
    All fields are optional since partial updates are allowed.
    """
    name: str | None = Field(
        None,
        description="New first name for the user",
        min_length=1,
        max_length=50,
        example="John"
    )
    surname: str | None = Field(
        None,
        description="New last name for the user",
        min_length=1,
        max_length=50,
        example="Smith"
    )
    preferences: list[int] | None = Field(
        None,
        description="Updated list of genre IDs for user's movie preferences",
        min_items=0,
        max_items=20,
        example=[28, 14, 35]
    )

    class Config:
        json_schema_extra = {
            "description": "Model for updating user information - all fields optional",
            "examples": [
                {
                    "preferences": [28, 14]  # Example of updating only preferences
                },
                {
                    "name": "John",
                    "surname": "Smith",
                    "preferences": [28, 14, 35]  # Example of full update
                }
            ]
        }