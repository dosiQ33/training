from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from .schemas import UserCreate, UserUpdate

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()

async def get_user_by_id(session: AsyncSession, user_id: int):
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, user: UserCreate):
    db_user = User(**user.model_dump())
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

async def update_user(session: AsyncSession, telegram_id: int, user: UserUpdate):
    db_user = await get_user_by_telegram_id(session, telegram_id)
    if not db_user:
        return None

    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)

    await session.commit()
    await session.refresh(db_user)
    return db_user
