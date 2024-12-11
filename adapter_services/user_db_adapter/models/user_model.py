from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from bson import ObjectId
import re
from PyObjectId import PyObjectId
from UserRole import UserRole
from config.config import db

class UserModel(BaseModel):
    """
    Pydantic model for user data with comprehensive validation
    """
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(
        ...,  # Required field
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_]+$'  # Alphanumeric and underscore
    )
    email: EmailStr  # Validates email format
    full_name: Optional[str] = Field(
        default=None,
        max_length=100
    )
    role: str = Field(
        default=UserRole.USER,
        pattern=f"^({UserRole.ADMIN}|{UserRole.USER})$"
    )
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    hashed_password: str  # Store hashed passwords only!
    created_at: datetime = Field(default_factory=datetime.now(datetime.timezone.utc))
    updated_at: Optional[datetime] = None
    # profile_image_url: Optional[str] = Field(
    #     default=None,
    #     pattern=r'^(https?://\S+\.(jpg|jpeg|png|gif))$'
    # )
    favorite_categories: Optional[List[str]] = Field(
        default_factory=list,
        max_items=10
    )

    class Config:
        """Pydantic model configuration"""
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string when serializing
        }
        orm_mode = True  # For compatibility with ORMs

    @field_validator('username')
    def validate_username(cls, v):
        """Additional username validation"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric or underscore')
        return v

    @field_validator('favorite_categories')
    def validate_interests(cls, v):
        """Validate interests list"""
        if v:
            # Ensure no duplicates and trim whitespace
            return list(set(favorite_categories.strip() for favorite_categories in v))
        return v

    def update_last_modified(self):
        """
        Method to update the last modified timestamp
        """
        self.updated_at = datetime.now(datetime.timezone.utc)

users = db.users