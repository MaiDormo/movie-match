from fastapi import HTTPException, Depends, Query, status, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from bson import ObjectId
from models.genre_model import Genre, GenreUpdate
import os

class Settings(BaseModel):
    db_uri: str = os.getenv("ATLAS_URI")
    db_name: str = os.getenv("DB_NAME", "movie-match")
    db_collection: str = "genres"

def get_settings() -> Settings:
    """Get database settings."""
    return Settings()

def get_collection(settings: Settings = Depends(get_settings)):
    """Get MongoDB collection with error handling."""
    try:
        client = MongoClient(settings.db_uri)
        # Test connection
        client.admin.command('ping')
        return client[settings.db_name][settings.db_collection]
    except ServerSelectionTimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection timed out"
        ) from e
    except OperationFailure as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database operation failed"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        ) from e

def create_response(status_code: int, message: str, data: dict = None) -> JSONResponse:

    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data

    return JSONResponse(content=content, status_code=status_code)

def serialize_genre(genre):
    """Convert MongoDB document to JSON serializable dict."""
    genre['_id'] = str(genre['_id'])
    return genre

async def health_check():
    return create_response(
        status_code=200, 
        message="The Genres API adapter is up and running!")

async def create_genre(genre: Genre, genres_collection = Depends(get_collection)) -> JSONResponse:
    """Create a new genre with an auto-incrementing integer ID."""
    try:
        # Find the highest existing ID
        highest_genre = genres_collection.find_one(
            {},
            sort=[("genreId", -1)]  # Sort by genreId in descending order
        )
        
        # Set new ID as highest + 1, or 1 if no genres exist
        new_id = (highest_genre["genreId"] + 1) if highest_genre else 1
        
        # Set the new ID in the genre model
        genre_dict = genre.model_dump(by_alias=True)
        genre_dict["genreId"] = new_id
        
        # Insert the genre with the new ID
        result = genres_collection.insert_one(genre_dict)
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create genre"
            )
            
        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="Genre created successfully",
            data=serialize_genre(genre_dict)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

async def list_genres(genres_collection = Depends(get_collection)) -> JSONResponse:
    """List all genres."""
    try:
        total = genres_collection.count_documents({})
        genres = [serialize_genre(genre) for genre in genres_collection.find()]
        
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Genres retrieved successfully",
            data={"total": total, "genres": genres}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve genres: {str(e)}"
        )

async def get_genre(id: int = Query(...), genres_collection = Depends(get_collection)) -> JSONResponse:
    """Get a specific genre by ID."""
    genre = genres_collection.find_one({"genreId": id})
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Genre with ID {id} not found"
        )
    
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Genre retrieved successfully",
        data=serialize_genre(genre)
    )

async def update_genre(
    id: int = Query(...),
    genre: GenreUpdate = Body(...),
    genres_collection = Depends(get_collection)
) -> JSONResponse:
    """Update a specific genre."""
    try:
        update_data = {k: v for k, v in genre.model_dump(by_alias=True).items() if v is not None}
        
        if not update_data:
            return create_response(
                status_code=status.HTTP_200_OK,
                message="No changes requested"
            )

        update_result = genres_collection.update_one(
            {"genreId": id},
            {"$set": update_data}
        )
        
        if update_result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Genre with ID {id} not found"
            )

        updated_genre = genres_collection.find_one({"genreId": update_data.get("genreId", id)})

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Genre updated successfully",
            data=serialize_genre(updated_genre)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

async def delete_genre(id: int = Query(...), genres_collection = Depends(get_collection)) -> JSONResponse:
    """Delete a specific genre."""
    result = genres_collection.delete_one({"genreId": id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Genre with ID {id} not found"
        )
        
    return create_response(
        status_code=status.HTTP_204_NO_CONTENT,
        message="Genre deleted successfully"
    )