import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class TokenType(str, Enum):  # Make TokenType inherit from str
    BEARER = "bearer"

class Settings(BaseModel):
    secret_key: str = os.getenv("SECRET_KEY", "")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

class Token(BaseModel):
    access_token: str
    token_type: TokenType

class LoginResponse(BaseModel):
    status: str
    data: Optional[Token] = None
    message: Optional[str] = None