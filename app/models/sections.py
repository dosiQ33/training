import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Numeric,
    DateTime,
    JSON,
    text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class SectionLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    pro = "pro"


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), index=True)

    name = Column(String(100), nullable=False)
    level = Column(String(20), nullable=True)  # хранится как str
    capacity = Column(Integer, nullable=True)  # макс. мест
    price = Column(Numeric(10, 2), nullable=True)
    duration_min = Column(Integer, nullable=True, server_default=text("60"))

    coach_id_default = Column(Integer, ForeignKey("users.id"), nullable=True)

    tags = Column(JSON, nullable=True, default=list)  # ["boxing", "kids"]
    schedule = Column(JSON, nullable=True, default=dict)  # см. пример ниже
    active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # relations
    club = relationship("Club", back_populates="sections")
