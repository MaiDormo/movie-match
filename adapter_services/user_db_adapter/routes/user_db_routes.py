from fastapi import APIRouter
from typing import List, Dict, Any, Optional
from controllers.user_db_controller import create_user, health_check, list_users, find_user, find_user_by_email, update_user, delete_user
from models.user_model import User, UserUpdate
from pydantic import BaseModel, Field

router = APIRouter()

# Response Models
class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class UserResponse(BaseResponse):
    data: Dict[str, Any] = Field(..., description="User details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "User retrieved successfully",
                "data": {
                    "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                    "name": "John",
                    "surname": "Doe",
                    "email": "john.doe@example.com",
                    "preferences": [28, 35]
                }
            }
        }

class UsersListResponse(BaseResponse):
    data: Dict[str, Any] = Field(..., description="List of users with pagination")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Users retrieved successfully",
                "data": {
                    "total": 2,
                    "users": [
                        {
                            "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                            "name": "John",
                            "surname": "Doe",
                            "email": "john.doe@example.com",
                            "preferences": [28, 35]
                        }
                    ]
                }
            }
        }

class ValidationError(BaseModel):
    field: str = Field(..., description="Path to the field that failed validation")
    message: str = Field(..., description="Description of the validation error")
    type: str = Field(..., description="Type of validation error")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "body -> email",
                "message": "field required",
                "type": "missing"
            }
        }

class ErrorResponse(BaseModel):
    status: str = Field(default="error", description="Error status indicator")
    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 422,
                "message": "Request validation failed",
                "details": [
                    {
                        "field": "body -> email",
                        "message": "field required",
                        "type": "missing"
                    }
                ]
            }
        }

router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the User DB API adapter service is running",
    responses={
        200: {
            "description": "Service is running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User DB API adapter is up and running"
                    }
                }
            }
        },
        405: {
            "description": "Method not allowed",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Method not allowed"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal server error occurred"
                    }
                }
            }
        }
    }
)(health_check)

router.post(
    "/api/v1/user",
    status_code=201,
    response_model=UserResponse,
    summary="Create User",
    description="Create a new user in the database",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User created successfully",
                        "data": {
                            "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                            "name": "John",
                            "surname": "Doe",
                            "email": "john.doe@example.com",
                            "preferences": [28, 35]
                        }
                    }
                }
            }
        },
        400: {
            "description": "Email already registered",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Email already registered"
                    }
                }
            }
        },
        405: {
            "description": "Method not allowed",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Method not allowed"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 422,
                        "message": "Request validation failed",
                        "details": [
                            {
                                "field": "body -> email",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal server error occurred"
                    }
                }
            }
        },
        503: {
            "description": "Database connection error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Database connection error"
                    }
                }
            }
        }
    }
)(create_user)

router.get(
    "/api/v1/users",
    response_model=UsersListResponse,
    summary="List Users",
    description="Get list of all users with pagination",
    responses={
        200: {
            "description": "Users retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Users retrieved successfully",
                        "data": {
                            "total": 2,
                            "users": [
                                {
                                    "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                                    "name": "John",
                                    "surname": "Doe",
                                    "email": "john.doe@example.com",
                                    "preferences": [28, 35]
                                }
                            ]
                        }
                    }
                }
            }
        },
        404: {
            "description": "No users found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "No users found"
                    }
                }
            }
        },
        405: {
            "description": "Method not allowed",
            "content": {
                "application/json": {
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 422,
                        "message": "Request validation failed",
                        "details": [
                            {
                                "field": "query -> page",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal server error occurred"
                    }
                }
            }
        },
        503: {
            "description": "Database connection error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Database connection error"
                    }
                }
            }
        }
    }
)(list_users)

router.get(
    "/api/v1/user",
    response_model=UserResponse,
    summary="Get User",
    description="Get a specific user by ID",
    responses={
        200: {
            "description": "User retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User retrieved successfully",
                        "data": {
                            "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                            "name": "John",
                            "surname": "Doe",
                            "email": "john.doe@example.com",
                            "preferences": [28, 35]
                        }
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "User not found"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 422,
                        "message": "Request validation failed",
                        "details": [
                            {
                                "field": "query -> id",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal server error", 
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal server error occurred"
                    }
                }
            }
        },
        503: {
            "description": "Database connection error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Database connection error"
                    }
                }
            }
        }
    }
)(find_user)

router.get(
    "/api/v1/user-email",
    response_model=UserResponse,
    summary="Get User by Email",
    description="Get a specific user by email address",
    responses={
        200: {
            "description": "User retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User retrieved successfully",
                        "data": {
                            "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                            "name": "John",
                            "surname": "Doe",
                            "email": "john.doe@example.com",
                            "preferences": [28, 35]
                        }
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "User not found"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 422,
                        "message": "Request validation failed",
                        "details": [
                            {
                                "field": "query -> email",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal server error occurred"
                    }
                }
            }
        },
        503: {
            "description": "Database connection error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Database connection error"
                    }
                }
            }
        }
    }
)(find_user_by_email)

router.put(
    "/api/v1/user",
    response_model=UserResponse,
    summary="Update User",
    description="Update an existing user by ID",
    responses={
        200: {
            "description": "User updated successfully or no changes needed",
            "content": {
                "application/json": {
                    "examples": {
                        "updated": {
                            "summary": "User updated",
                            "value": {
                                "status": "success",
                                "message": "User updated successfully",
                                "data": {
                                    "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                                    "name": "John",
                                    "surname": "Doe",
                                    "email": "john.updated@example.com",
                                    "preferences": [28, 35, 12]
                                }
                            }
                        },
                        "no_changes": {
                            "summary": "No changes needed",
                            "value": {
                                "status": "success",
                                "message": "No changes requested"
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "User not found"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 422,
                        "message": "Request validation failed",
                        "details": [
                            {
                                "field": "query -> id",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal server error occurred"
                    }
                }
            }
        },
        503: {
            "description": "Database connection error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Database connection error"
                    }
                }
            }
        }
    }
)(update_user)

router.delete(
    "/api/v1/user",
    status_code=204,
    summary="Delete User", 
    description="Delete a user by ID",
    responses={
        204: {
            "description": "User deleted successfully"
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "User not found"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 422,
                        "message": "Request validation failed",
                        "details": [
                            {
                                "field": "query -> id",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal server error occurred"
                    }
                }
            }
        },
        503: {
            "description": "Database connection error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Database connection error"
                    }
                }
            }
        }
    }
)(delete_user)