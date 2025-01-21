from pydantic import BaseModel, Field


class Genre(BaseModel):
    genre_id: int | None = Field(default=None, alias="genreId") #gets autogenerated in function create
    name: str = Field(..., description="The name of the genre")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "name": "Action"  # _id is not needed in the example since it's auto-generated
            }
        }

class GenreUpdate(BaseModel):
    genre_id: int | None = Field(None, alias="genreId", description="The genre ID")
    name: int | None = Field(None, description="The name of the genre")

    class config: 
        json_schema_extra = {
            "example": {
                ""
                "genreId": 878,
                "name": "Sci-Fi" #from the original Science Fiction
            }
        }

