import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_session
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserRead,
    UserListResponse,
    PreferencesUpdate,
    UserFilters,
)

from app.crud import (
    get_user_by_id,
    get_user_by_telegram_id,
    get_users_paginated,
    create_user,
    update_user,
    update_user_preferences,
    get_user_preference,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    existing = await get_user_by_telegram_id(db, user.telegram_id)
    if existing:
        raise HTTPException(
            status_code=409, detail="User with this telegram_id already exists."
        )
    return await create_user(db, user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_session)):
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=UserListResponse)
async def get_users_list(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    # Фильтры как query параметры
    first_name: Optional[str] = Query(
        None, description="Filter by first name (partial match)"
    ),
    last_name: Optional[str] = Query(
        None, description="Filter by last name (partial match)"
    ),
    phone_number: Optional[str] = Query(
        None, description="Filter by phone number (partial match)"
    ),
    role: Optional[str] = Query(None, description="Filter by role (exact match)"),
    username: Optional[str] = Query(
        None, description="Filter by username (partial match)"
    ),
    db: AsyncSession = Depends(get_session),
):
    skip = (page - 1) * size

    # Создаем объект фильтров
    filters = UserFilters(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        role=role,
        username=username,
    )

    # Если все фильтры пустые, передаем None
    if not any([first_name, last_name, phone_number, role, username]):
        filters = None

    users, total = await get_users_paginated(db, skip=skip, limit=size, filters=filters)

    pages = math.ceil(total / size) if total > 0 else 1

    return UserListResponse(
        users=users, total=total, page=page, size=size, pages=pages, filters=filters
    )


@router.get("/by-telegram-id/{telegram_id}", response_model=UserRead)
async def get_user_by_telegram_id_route(
    telegram_id: int, db: AsyncSession = Depends(get_session)
):
    user = await get_user_by_telegram_id(db, telegram_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{telegram_id}", response_model=UserRead)
async def update_user_by_telegram_id(
    telegram_id: int, user: UserUpdate, db: AsyncSession = Depends(get_session)
):
    db_user = await update_user(db, telegram_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{telegram_id}/preferences", response_model=UserRead)
async def update_user_preferences_route(
    telegram_id: int,
    preferences: PreferencesUpdate,
    db: AsyncSession = Depends(get_session),
):
    """Update user preferences (language, dark_mode, notifications, timezone)"""
    db_user = await update_user_preferences(db, telegram_id, preferences)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/{telegram_id}/preferences/{preference_key}")
async def get_user_preference_route(
    telegram_id: int, preference_key: str, db: AsyncSession = Depends(get_session)
):
    """Get specific user preference by key"""
    preference_value = await get_user_preference(db, telegram_id, preference_key)
    if preference_value is None:
        raise HTTPException(status_code=404, detail="User or preference not found")

    return {
        "telegram_id": telegram_id,
        "preference_key": preference_key,
        "value": preference_value,
    }
