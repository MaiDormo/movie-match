from fastapi import Body, Request, Response, HTTPException, status, Query, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from models.user_model import User, UserUpdate
from passlib.context import CryptContext
from pymongo.collection import Collection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_collection(request: Request) -> Collection:
    return request.app.database["movie-match"]["users"]

async def health_check() -> JSONResponse:
    response = {
        "status": "success",
        "message": "User DB API Adapter is up and running!"
    }
    return JSONResponse(content=response, status_code=200)

async def create_user(user: User = Body(...), users_collection: Collection = Depends(get_user_collection)) -> JSONResponse:
    user = jsonable_encoder(user)
    # Hash password before storing
    user["password"] = pwd_context.hash(user["password"])
    if users_collection.find_one({"email": user["email"]}):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = users_collection.insert_one(user)
    created_user = users_collection.find_one({"_id": new_user.inserted_id})
    if created_user is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User creation failed")
    return JSONResponse(content=created_user, status_code=status.HTTP_201_CREATED)

async def list_users(limit: int = 100, offset: int = 0, users_collection: Collection = Depends(get_user_collection)) -> JSONResponse:
    total = users_collection.count_documents({})
    users = list(users_collection.find().skip(offset).limit(limit))
    return JSONResponse(content={
        "total": total,
        "offset": offset,
        "limit": limit,
        "users": users
    }, status_code=200)

async def find_user(id: str = Query(...), users_collection: Collection = Depends(get_user_collection)) -> JSONResponse:
    user = users_collection.find_one({"_id": id})
    if user is not None:
        return JSONResponse(content=user, status_code=200)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

async def find_user_by_email(email: str = Query(...), users_collection: Collection = Depends(get_user_collection)) -> JSONResponse:
    user = users_collection.find_one({"email": email})
    if user is not None:
        return JSONResponse(content=user, status_code=200)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {email} not found")

async def update_user(id: str = Query(...), user: UserUpdate = Body(...), users_collection: Collection = Depends(get_user_collection)) -> JSONResponse:
    user_data = {k: v for k, v in user.model_dump().items() if v is not None}
    if len(user_data) >= 1:
        update_result = users_collection.update_one({"_id": id}, {"$set": user_data})
        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

    existing_user = users_collection.find_one({"_id": id})
    if existing_user is not None:
        return JSONResponse(content=existing_user, status_code=200)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

async def delete_user(id: str = Query(...), users_collection: Collection = Depends(get_user_collection)) -> Response:
    delete_result = users_collection.delete_one({"_id": id})
    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")