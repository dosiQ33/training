from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    language: Optional[str] = "ru"
    dark_mode: Optional[bool] = False
    notifications: Optional[bool] = True
    timezone: Optional[str] = "UTC+5"


class UserBase(BaseModel):
    telegram_id: int
    first_name: str
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserCreate(BaseModel):
    phone_number: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    username: Optional[str] = None


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserFilters(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    username: Optional[str] = None


class UserListResponse(BaseModel):
    users: list[UserRead]
    total: int
    page: int
    size: int
    pages: int
    filters: Optional[UserFilters] = None


class PreferencesUpdate(BaseModel):
    language: Optional[str] = None
    dark_mode: Optional[bool] = None
    notifications: Optional[bool] = None
    timezone: Optional[str] = None
