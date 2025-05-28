from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    phone_number = Column(String(30), nullable=True)
    username = Column(String(64), nullable=True, index=True)
    role = Column(String(16), nullable=False, default="student")
    preferences = Column(JSON, nullable=True, default={})
    avatar_url = Column(String(256), nullable=True)
    language = Column(String(8), nullable=False, default="KZ")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
