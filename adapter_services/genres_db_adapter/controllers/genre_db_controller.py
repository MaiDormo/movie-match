from typing import Collection, Dict, Any
from fastapi import HTTPException, Depends, Query, Request, status, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from models.genre_model import Genre, GenreUpdate
import os

# Config Models
class Settings(BaseModel):
    db_name: str = os.getenv("DB_NAME", "movie-match")
    db_collection: str = "genres"

# Database Helpers
def get_settings() -> Settings:
    return Settings()

def get_collection(request: Request, settings: Settings = Depends(get_settings)) -> Collection:
    mongo_client = request.app.state.db
    return mongo_client[settings.db_name][settings.db_collection]

# Response Helpers
def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

def serialize_genre(genre: Dict[str, Any]) -> Dict[str, Any]:
    genre['_id'] = str(genre['_id'])
    return genre

# Controller Functions
async def health_check() -> JSONResponse:
    return create_response(
        status_code=status.HTTP_200_OK,
        message="The Genres API adapter is up and running!"
    )

async def create_genre(
    genre: Genre, 
    genres_collection: Collection = Depends(get_collection)
) -> JSONResponse:
    try:
        # Find highest existing ID
        highest_genre = genres_collection.find_one({}, sort=[("genreId", -1)])
        new_id = (highest_genre["genreId"] + 1) if highest_genre else 1
        
        # Prepare and insert genre
        genre_dict = genre.model_dump(by_alias=True)
        genre_dict["genreId"] = new_id
        result = genres_collection.insert_one(genre_dict)
        
        if not result.inserted_id:
            raise create_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to create genre"
            )
        
        created_genre = genres_collection.find_one({"_id": result.inserted_id})
        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="Genre created successfully",
            data=serialize_genre(created_genre)
        )
    except Exception as e:
        raise create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e)
        )

async def list_genres(
    genres_collection: Collection = Depends(get_collection)
) -> JSONResponse:
    try:
        genres = [serialize_genre(genre) for genre in genres_collection.find()]
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Genres retrieved successfully",
            data={
                "total": len(genres),
                "genres": genres
            }
        )
    except Exception as e:
        raise create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to retrieve genres: {str(e)}"
        )

async def get_genre(
    id: int = Query(...), 
    genres_collection: Collection = Depends(get_collection)
) -> JSONResponse:
    genre = genres_collection.find_one({"genreId": id})
    if not genre:
        raise create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Genre with ID {id} not found"
        )
    
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Genre retrieved successfully",
        data=serialize_genre(genre)
    )

async def update_genre(
    id: int = Query(...),
    genre: GenreUpdate = Body(...),
    genres_collection: Collection = Depends(get_collection)
) -> JSONResponse:
    try:
        update_data = {
            k: v for k, v in genre.model_dump(
                by_alias=True, 
                exclude_unset=True, 
                exclude_none=True
            ).items()
        }
        
        if not update_data:
            return create_response(
                status_code=status.HTTP_200_OK,
                message="No changes requested"
            )

        result = genres_collection.update_one(
            {"genreId": id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"Genre with ID {id} not found"
            )

        updated_genre = genres_collection.find_one({"genreId": id})
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Genre updated successfully",
            data=serialize_genre(updated_genre)
        )
    except Exception as e:
        raise create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e)
        )

async def delete_genre(
    id: int = Query(...), 
    genres_collection: Collection = Depends(get_collection)
) -> JSONResponse:
    result = genres_collection.delete_one({"genreId": id})
    
    if result.deleted_count == 0:
        raise create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Genre with ID {id} not found"
        )
        
    return create_response(
        status_code=status.HTTP_204_NO_CONTENT,
        message="Genre deleted successfully"
    )