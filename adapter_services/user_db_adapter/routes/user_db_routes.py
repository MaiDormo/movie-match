from fastapi import APIRouter
from typing import List
from controllers.user_db_controller import create_user, health_check, list_users, find_user, find_user_by_email, update_user, delete_user, update_user_preferences
from models.user_model import User, UserUpdate

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.post("/api/v1/user", response_model=User)(create_user)
router.get("/api/v1/users", response_model=List[User])(list_users)
router.get("/api/v1/user", response_model=User)(find_user)
router.get("/api/v1/user-email", response_model=User)(find_user_by_email)
router.put("/api/v1/user", response_model=User)(update_user)
router.delete("/api/v1/user")(delete_user)
router.put("/api/v1/user-preferences")(update_user_preferences)