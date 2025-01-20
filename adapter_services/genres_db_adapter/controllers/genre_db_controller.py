from typing import Collection
from fastapi import HTTPException, Depends, Query, Request, status, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from models.genre_model import Genre, GenreUpdate
import os


from config.database import get_mongo_client

class Settings(BaseModel):
    db_name: str = os.getenv("DB_NAME", "movie-match")
    db_collection: str = "genres"

def get_settings() -> Settings:
    """Get database settings."""
    return Settings()

def get_collection(request: Request, settings: Settings = Depends(get_settings)) -> Collection:
    """Get MongoDB collection from request app state."""
    mongo_client = request.app.state.db
    return mongo_client[settings.db_name][settings.db_collection]


def serialize_genre(genre):
    """Convert MongoDB document to JSON serializable dict."""
    genre['_id'] = str(genre['_id'])
    return genre

async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "success",
            "message": "The Genres API adapter is up and running!"
        },
        status_code=status.HTTP_200_OK
    )

async def create_genre(genre: Genre, genres_collection = Depends(get_collection)) -> JSONResponse:
    """Create a new genre with an auto-incrementing integer ID."""
    try:
        # Find the highest existing ID
        highest_genre = genres_collection.find_one(
            {},
            sort=[("genreId", -1)]
        )
        
        # Set new ID as highest + 1, or 1 if no genres exist
        new_id = (highest_genre["genreId"] + 1) if highest_genre else 1
        
        # Prepare genre document
        genre_dict = genre.model_dump(by_alias=True)
        genre_dict["genreId"] = new_id
        
        # Insert genre
        result = genres_collection.insert_one(genre_dict)
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create genre"
            )
        
        # Get created genre
        created_genre = genres_collection.find_one({"_id": result.inserted_id})
        return JSONResponse(
            content={
                "status": "success",
                "message": "Genre created successfully",
                "data": serialize_genre(created_genre)
            },
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def list_genres(genres_collection = Depends(get_collection)) -> JSONResponse:
    """List all genres."""
    try:
        genres = [serialize_genre(genre) for genre in genres_collection.find()]
        return JSONResponse(
            content={
                "status": "success", 
                "message": "Genres retrieved successfully",
                "data": {
                    "total": len(genres),
                    "genres": genres
                }
            },
            status_code=status.HTTP_200_OK
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
    
    return JSONResponse(
        content={
            "status": "success",
            "message": "Genre retrieved successfully",
            "data": serialize_genre(genre)
        },
        status_code=status.HTTP_200_OK
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
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "No changes requested"
                },
                status_code=status.HTTP_200_OK
            )

        result = genres_collection.update_one(
            {"genreId": id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Genre with ID {id} not found"
            )

        updated_genre = genres_collection.find_one({"genreId": id})
        return JSONResponse(
            content={
                "status": "success",
                "message": "Genre updated successfully",
                "data": serialize_genre(updated_genre)
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        
    return JSONResponse(
        content={
            "status": "success",
            "message": "Genre deleted successfully"
        },
        status_code=status.HTTP_204_NO_CONTENT
    )