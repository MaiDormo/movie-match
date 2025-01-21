from fastapi import APIRouter
from typing import List
from controllers.user_db_controller import create_user, health_check, list_users, find_user, find_user_by_email, update_user, delete_user
from models.user_model import User, UserUpdate

router = APIRouter()

# Health check returns a dict
router.get("/", response_model=dict)(health_check)

# User operations return a dict with status, message, and data
router.post("/api/v1/user", response_model=dict)(create_user)
router.get("/api/v1/users", response_model=dict)(list_users)
router.get("/api/v1/user", response_model=dict)(find_user)
router.get("/api/v1/user-email", response_model=dict)(find_user_by_email)
router.put("/api/v1/user", response_model=dict)(update_user)
router.delete("/api/v1/user", response_model=dict)(delete_user)