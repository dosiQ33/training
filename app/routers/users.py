from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_session
from app.schemas import UserCreate, UserUpdate, UserRead
from app.crud import (
    get_user_by_id,
    get_user_by_telegram_id,
    create_user,
    update_user,
)

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_session)
):
    existing = await get_user_by_telegram_id(db, user.telegram_id)
    if existing:
        raise HTTPException(status_code=409, detail="User with this telegram_id already exists.")
    return await create_user(db, user)

@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_session)
):
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/by-telegram-id/{telegram_id}", response_model=UserRead)
async def get_user_by_telegram_id_route(
    telegram_id: int,
    db: AsyncSession = Depends(get_session)
):
    user = await get_user_by_telegram_id(db, telegram_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{telegram_id}", response_model=UserRead)
async def update_user_by_telegram_id(
    telegram_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_session)
):
    db_user = await update_user(db, telegram_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
