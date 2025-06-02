from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(Base):
    """
    Таблица RBAC: одна запись = одна роль пользователя в конкретном клубе.
    """

    __tablename__ = "user_roles"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    club_id = Column(
        Integer, ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True
    )
    role_id = Column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )

    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    # relationships
    user = relationship("User", back_populates="roles")
    club = relationship("Club", back_populates="user_roles")
    role = relationship("Role")

    __table_args__ = (Index("ix_user_roles_user_club", "user_id", "club_id"),)
