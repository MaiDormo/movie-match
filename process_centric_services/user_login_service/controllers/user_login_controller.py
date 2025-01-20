from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from typing import Annotated, Optional, Dict, Any
import requests
import jwt
from datetime import datetime, timedelta
import pytz
from schemas.user_login_schemas import *

# Constants
USER_DB_ADAPTER = "http://user-db-adapter:5000/api/v1/user-email"
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="login")

def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

def create_response(
    status_code: int, 
    message: str, 
    data: Dict[str, Any] = None, 
    status: str = "success"
) -> JSONResponse:
    """Create a standardized JSON response."""
    content = {"status": status, "message": message}
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="User Login Service is up and running!"
    )

def verify_token(token: str, settings: Settings = Depends(get_settings)) -> str:
    """Verify JWT token and return email."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if email := payload.get("sub"):
            return email
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token: missing subject claim"
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

def create_access_token(
    data: Dict[str, Any], 
    settings: Settings, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(pytz.UTC) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    try:
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating access token: {str(e)}"
        )

async def validate_credentials(email: str, password: str) -> Dict[str, Any]:
    """Validate user credentials against the database."""
    try:
        response = requests.get(
            USER_DB_ADAPTER, 
            params={"email": email}, 
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found. Please check your email and try again."
            )
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error validating credentials: {str(http_err)}"
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Database service timeout"
        )
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database service error: {str(req_err)}"
        )

async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """Handle user login and return access token."""
    # Validate input
    if not form_data.username or not form_data.password:
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Email and password are required",
            status="fail"
        )

    # Validate credentials
    user_data = await validate_credentials(form_data.username, form_data.password)

    # Verify password
    if not PWD_CONTEXT.verify(form_data.password, user_data["data"]["password"]):
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid password",
            status="fail"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": form_data.username},
        settings=settings,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    # Return success response
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Login successful",
        data=Token(
            access_token=access_token,
            token_type=TokenType.BEARER
        ).model_dump()
    )

async def refresh_token(
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """Refresh an existing access token."""
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing token: {str(e)}"
        )