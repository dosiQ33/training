from pydantic import BaseModel

class UserBase(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str | None = None
    phone_number: str | None = None
    username: str | None = None
    role: str | None = None
    
class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    username: str | None = None
    role: str | None = None

class UserRead(UserCreate):
    id: int

    class Config:
        from_attributes = True
