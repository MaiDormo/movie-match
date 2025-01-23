from pydantic import BaseModel, Field


class Genre(BaseModel):
    """
    Represents a movie genre in the database.
    
    This model is used for creating and retrieving genre information.
    The genreId is auto-generated during creation.
    """
    genre_id: int | None = Field(
        default=None, 
        alias="genreId",
        description="Unique identifier for the genre (auto-generated)",
        example=28
    )
    name: str = Field(
        ..., 
        description="The name of the genre",
        min_length=1,
        max_length=50,
        example="Action"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "description": "A movie genre with a unique identifier and name",
            "example": {
                "genreId": 28,
                "name": "Action"
            }
        }


class GenreUpdate(BaseModel):
    """
    Represents a genre update request.
    
    This model is used for updating existing genres.
    All fields are optional since partial updates are allowed.
    """
    genre_id: int | None = Field(
        None, 
        alias="genreId", 
        description="The unique identifier of the genre to update",
        example=878,
        ge=1
    )
    name: str | None = Field(  # Fixed: Changed int to str for name field
        None, 
        description="The new name for the genre",
        min_length=1,
        max_length=50,
        example="Sci-Fi"
    )

    class Config:  # Fixed: Changed 'config' to 'Config'
        populate_by_name = True
        json_schema_extra = {
            "description": "Fields to update for an existing genre",
            "example": {
                "genreId": 878,
                "name": "Sci-Fi"  # Updated from Science Fiction
            }
        }