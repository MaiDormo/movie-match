from fastapi import Depends, status, Query, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from typing import Annotated, Optional, Dict, Any
from pydantic import Field
import requests
import jwt
from datetime import datetime, timedelta
import pytz
from schemas.user_login_schemas import *

class AuthConfig:
    """Authentication configuration and constants"""
    USER_DB_ADAPTER = "http://user-db-adapter:5000/api/v1/user-email"
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
    OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="login")
    REQUEST_TIMEOUT = 10

def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

def create_response(
    status_code: int = Field(..., description="HTTP status code for the response"),
    message: str = Field(..., description="Response message"),
    data: Dict[str, Any] = Field(None, description="Optional response data")
) -> JSONResponse:
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
        message="User Login Service is up and running!"
    )

def verify_token(
    token: str = Field(..., description="JWT token to verify"), 
    settings: Settings = Depends(get_settings)
) -> str:
    """
    Verify JWT token and return email.

    Args:
        token: JWT token string
        settings: Application settings containing JWT configuration

    Returns:
        str: Email address from token if valid
        JSONResponse: Error response if token is invalid
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if email := payload.get("sub"):
            return email
        return create_response(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            message="Invalid token: missing subject claim"
        )
    except jwt.ExpiredSignatureError:
        return create_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Token has expired"
        )
    except jwt.InvalidTokenError:
        return create_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token format"
        )

def create_access_token(
    data: Dict[str, Any] = Field(..., description="Data to encode in the token"),
    settings: Settings = Field(..., description="Application settings"),
    expires_delta: Optional[timedelta] = Field(
        None, 
        description="Token expiration time. Defaults to 15 minutes if not provided"
    )
) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(pytz.UTC) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    try:
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error creating access token: {str(e)}"
        )

async def validate_credentials(
    email: str = Query(
        ..., 
        description="User's email address",
        example="user@example.com"
    ),
    password: str = Query(
        ..., 
        description="User's password",
        min_length=8
    )
) -> Dict[str, Any]:
    """Validate user credentials against the database."""
    try:
        response = requests.get(
            AuthConfig.USER_DB_ADAPTER, 
            params={"email": email}, 
            timeout=AuthConfig.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Email not found. Please check your email and try again."
            )
        return create_response(
            status_code=response.status_code,
            message=f"Error validating credentials: {str(http_err)}"
        )
    except requests.exceptions.Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Database service timeout"
        )
    except requests.exceptions.RequestException as req_err:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database service error: {str(req_err)}"
        )

async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """Handle user login and return access token."""
    if not form_data.username or not form_data.password:
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Email and password are required",
        )

    user_data = await validate_credentials(form_data.username, form_data.password)

    if isinstance(user_data, JSONResponse):
        return user_data

    if not AuthConfig.PWD_CONTEXT.verify(form_data.password, user_data["data"]["password"]):
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid password",
        )

    access_token = create_access_token(
        data={"sub": form_data.username},
        settings=settings,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Login successful",
        data=Token(
            access_token=access_token,
            token_type=TokenType.BEARER
        ).model_dump()
    )

async def refresh_token(
    token: Annotated[
        str, 
        Depends(AuthConfig.OAUTH2_SCHEME),
        Field(..., description="Current valid JWT token")
    ],
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """
    Refresh an existing access token.
    
    Args:
        token: Current valid JWT token
        settings: Application settings containing JWT configuration

    Returns:
        JSONResponse: New access token if successful, error response otherwise
    """
    try:
        email = verify_token(token, settings)
        new_access_token = create_access_token(
            data={"sub": email},
            settings=settings,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Token refreshed successfully",
            data=Token(
                access_token=new_access_token,
                token_type=TokenType.BEARER
            ).model_dump()
        )
    except create_response:
        return
    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error refreshing token: {str(e)}"
        )