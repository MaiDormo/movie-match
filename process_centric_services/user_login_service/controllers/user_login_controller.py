from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Annotated
import requests
import jwt
import os
from datetime import datetime, timedelta
import pytz

class Settings(BaseModel):
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def get_settings():
    return Settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

USER_DB_ADAPTER = "http://user-db-adapter:5000/api/v1/user-email"

async def health_check() -> JSONResponse:
    return JSONResponse(content={
        "status": "success",
        "message": "User Login Service is up and running!"
    }, status_code=200)

def verify_token(token: str, settings: Settings = Depends(get_settings)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_access_token(data: dict, settings: Settings, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(pytz.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, key=settings.secret_key, algorithm=settings.algorithm)

async def login(form_data: OAuth2PasswordRequestForm = Depends(), settings: Settings = Depends(get_settings)):
    email, password = form_data.username, form_data.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        response = requests.get(USER_DB_ADAPTER, params={"email": email})
        response.raise_for_status()
        external_data = response.json()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Email not found. Please check your email and try again.")
        raise HTTPException(status_code=response.status_code, detail=f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(status_code=500, detail=f"An error occurred: {req_err}")

    if not pwd_context.verify(password, external_data["password"]):
        return JSONResponse(content={
            "status": "fail",
            "data": {"password": "Passwords do not match!"}
        }, status_code=400)

    access_token = create_access_token(
        data={"sub": email},
        settings=settings,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return JSONResponse(content={
        "status": "success",
        "data": {
            "access_token": access_token,
            "token_type": "bearer"
        }
    }, status_code=200)

async def refresh_token(token: Annotated[str, Depends(oauth2_scheme)], settings: Settings = Depends(get_settings)):
    email = verify_token(token, settings)
    new_access_token = create_access_token(
        data={"sub": email},
        settings=settings,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return JSONResponse(content={
        "status": "success",
        "data": {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    }, status_code=200)