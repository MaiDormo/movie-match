import os
from fastapi import Body, Request, status, Query, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List, Dict, Any

from pydantic import BaseModel
from models.user_model import User, UserUpdate
from passlib.context import CryptContext
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from config.databse import get_mongo_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Settings(BaseModel):
    db_name: str = os.getenv("DB_NAME", "movie-match")
    db_collection: str = "users"

def get_settings():
    """Get database settings."""
    return Settings()

def get_user_collection(request: Request, settings: Settings = Depends(get_settings)) -> Collection:
    """Get MongoDB users collection from request app state."""
    mongo_client = request.app.state.db
    return mongo_client[settings.db_name][settings.db_collection]

def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="User DB API Adapter is up and running!"
    )

async def create_user(
    user: User = Body(...), 
    users_collection: Collection = Depends(get_user_collection)
) -> JSONResponse:
    """Create a new user."""
    try:
        user_dict = jsonable_encoder(user)
        user_dict["password"] = pwd_context.hash(user_dict["password"])
        
        # Check for existing email
        if users_collection.find_one({"email": user_dict["email"]}):
            return create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Email already registered"
            )
        
        # Insert new user
        result = users_collection.insert_one(user_dict)
        if not result.inserted_id:
            return create_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to create user"
            )
        
        created_user = users_collection.find_one({"_id": result.inserted_id})
        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="User created successfully",
            data=created_user
        )
        
    except DuplicateKeyError:
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="A user with this ID already exists"
        )
    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e)
        )

async def list_users(
    limit: int = 100, 
    offset: int = 0, 
    users_collection: Collection = Depends(get_user_collection)
) -> JSONResponse:
    """List all users with pagination."""
    try:
        total = users_collection.count_documents({})
        users = list(users_collection.find().skip(offset).limit(limit))
        
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Users retrieved successfully",
            data={
                "total": total,
                "offset": offset,
                "limit": limit,
                "users": users
            }
        )
    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to retrieve users: {str(e)}"
        )

async def find_user(
    id: str = Query(...), 
    users_collection: Collection = Depends(get_user_collection)
) -> JSONResponse:
    """Find a user by ID."""
    user = users_collection.find_one({"_id": id})
    if not user:
        return create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"User with ID {id} not found"
        )
    
    return create_response(
        status_code=status.HTTP_200_OK,
        message="User retrieved successfully",
        data=user
    )

async def find_user_by_email(
    email: str = Query(...), 
    users_collection: Collection = Depends(get_user_collection)
) -> JSONResponse:
    """Find a user by email."""
    user = users_collection.find_one({"email": email})
    if not user:
        return create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"User with email {email} not found"
        )
    
    return create_response(
        status_code=status.HTTP_200_OK,
        message="User retrieved successfully",
        data=user
    )

async def update_user(
    id: str = Query(...),
    user: UserUpdate = Body(...),
    users_collection: Collection = Depends(get_user_collection)
) -> JSONResponse:
    """Update a user by ID."""
    try:
        update_data = {k: v for k, v in user.model_dump(exclude_unset=True, exclude_none=True).items()}
        
        if not update_data:
            return create_response(
                status_code=status.HTTP_200_OK,
                message="No changes requested"
            )

        result = users_collection.update_one(
            {"_id": id}, 
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"User with ID {id} not found"
            )

        updated_user = users_collection.find_one({"_id": id})
        return create_response(
            status_code=status.HTTP_200_OK,
            message="User updated successfully",
            data=updated_user
        )
    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e)
        )

async def delete_user(
    id: str = Query(...), 
    users_collection: Collection = Depends(get_user_collection)
) -> JSONResponse:
    """Delete a user by ID."""
    result = users_collection.delete_one({"_id": id})
    
    if result.deleted_count == 0:
        return create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"User with ID {id} not found"
        )
    
    return create_response(
        status_code=status.HTTP_204_NO_CONTENT,
        message="User deleted successfully"
    )