from typing import List
from pydantic import BaseModel, Field

class UserRegistration(BaseModel):
    name: str = Field(...)
    surname: str = Field(...)
    email: str = Field(..., description="Must be a valid email address")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    password_confirmation: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    #TODO! decide on how to handle the preferences when registration: if start empty or start with some values

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John",
                "surname": "Doe",
                "email": "john.doe@example.com",
                "password": "securepassword123",
                "password_confirmation": "securepassword123"
            }
        }
