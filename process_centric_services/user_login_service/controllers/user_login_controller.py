from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from typing import Annotated, Optional
import requests
import jwt
import os
from datetime import datetime, timedelta
import pytz
from enum import Enum
from schemas.user_login_schemas import *

# Constants
USER_DB_ADAPTER = "http://user-db-adapter:5000/api/v1/user-email"
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="login")

def get_settings() -> Settings:
    return Settings()

async def health_check() -> JSONResponse:
    return JSONResponse(
        content={
            "status": "success",
            "message": "User Login Service is up and running!"
        },
        status_code=status.HTTP_200_OK
    )

def verify_token(token: str, settings: Settings = Depends(get_settings)) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if email := payload.get("sub"):
            return email
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )

def create_access_token(
    data: dict, 
    settings: Settings, 
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(pytz.UTC) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    email, password = form_data.username, form_data.password

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email and password are required"
        )

    try:
        response = requests.get(USER_DB_ADAPTER, params={"email": email}, timeout=10)
        response.raise_for_status()
        user_data = response.json()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found. Please check your email and try again."
            )
        raise HTTPException(
            status_code=response.status_code,
            detail=f"HTTP error occurred: {http_err}"
        )
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {req_err}"
        )

    if not PWD_CONTEXT.verify(password, user_data["password"]):
        return JSONResponse(
            content={
                "status": "fail",
                "message": "Invalid password"
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    access_token = create_access_token(
        data={"sub": email},
        settings=settings,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return JSONResponse(
        content=LoginResponse(
            status="success",
            data=Token(
                access_token=access_token,
                token_type=TokenType.BEARER
            )
        ).model_dump(),
        status_code=status.HTTP_200_OK
    )

async def refresh_token(
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    email = verify_token(token, settings)
    new_access_token = create_access_token(
        data={"sub": email},
        settings=settings,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return JSONResponse(
        content=LoginResponse(
            status="success",
            data=Token(
                access_token=new_access_token,
                token_type=TokenType.BEARER
            )
        ).model_dump(),
        status_code=status.HTTP_200_OK
    )