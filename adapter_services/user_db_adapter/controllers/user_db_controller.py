from fastapi import Body, Request, Response, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from models.user_model import User, UserUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def health_check() -> JSONResponse:
    response = {
        "status": "success",
        "message": "User DB API Adapter is up and running!"
    }
    return JSONResponse(content=response, status_code=200)

async def create_user(request: Request, user: User = Body(...)) -> JSONResponse:
    user = jsonable_encoder(user)
    # Hash password before storing
    user["password"] = pwd_context.hash(user["password"])
    if request.app.database["users"].find_one({"email": user["email"]}):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = request.app.database["users"].insert_one(user)
    created_user = request.app.database["users"].find_one({"_id": new_user.inserted_id})
    if created_user is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User creation failed")
    return JSONResponse(content=created_user, status_code=status.HTTP_201_CREATED)

async def list_users(request: Request, limit: int = 100, offset: int = 0) -> JSONResponse:
    total = request.app.database["users"].count_documents({})
    users = list(request.app.database["users"].find().skip(offset).limit(limit))
    return JSONResponse(content={
        "total": total,
        "offset": offset,
        "limit": limit,
        "users": users
    }, status_code=200)

async def find_user(request: Request, id: str = Query(...)) -> JSONResponse:
    user = request.app.database["users"].find_one({"_id": id})
    if user is not None:
        return JSONResponse(content=user, status_code=200)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

async def find_user_by_email(request: Request, email: str = Query(...)) -> JSONResponse:
    user = request.app.database["users"].find_one({"email": email})
    if user is not None:
        return JSONResponse(content=user, status_code=200)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {email} not found")

async def update_user(request: Request, id: str = Query(...), user: UserUpdate = Body(...)) -> JSONResponse:
    user_data = {k: v for k, v in user.model_dump().items() if v is not None}
    if len(user_data) >= 1:
        update_result = request.app.database["users"].update_one({"_id": id}, {"$set": user_data})
        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

    existing_user = request.app.database["users"].find_one({"_id": id})
    if existing_user is not None:
        return JSONResponse(content=existing_user, status_code=200)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

async def delete_user(request: Request, id: str = Query(...)) -> Response:
    delete_result = request.app.database["users"].delete_one({"_id": id})
    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")