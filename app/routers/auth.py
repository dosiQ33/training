from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me")
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user information.

    This endpoint requires Telegram authentication.
    In Swagger UI, click 'Authorize' and paste your Telegram initData.
    """
    return {
        "message": "Authentication successful!",
        "user": current_user,
        "telegram_id": current_user.get("id"),
        "first_name": current_user.get("first_name"),
        "last_name": current_user.get("last_name"),
        "username": current_user.get("username"),
        "language_code": current_user.get("language_code"),
        "photo_url": current_user.get("photo_url"),
    }


@router.post("/test")
async def test_auth(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Test endpoint to verify authentication works.
    """
    return {
        "status": "authenticated",
        "user_id": current_user.get("id"),
        "timestamp": "now",
    }
