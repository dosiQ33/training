from sqlalchemy import and_, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate, PreferencesUpdate, UserFilters


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int):
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_users_paginated(
    session: AsyncSession, skip: int = 0, limit: int = 10, filters: UserFilters = None
):
    # Базовый запрос
    base_query = select(User)
    count_query = select(func.count(User.id))

    # Применяем фильтры если они есть
    if filters:
        conditions = []

        if filters.first_name:
            conditions.append(User.first_name.ilike(f"%{filters.first_name}%"))

        if filters.last_name:
            conditions.append(User.last_name.ilike(f"%{filters.last_name}%"))

        if filters.phone_number:
            conditions.append(User.phone_number.ilike(f"%{filters.phone_number}%"))

        if filters.username:
            conditions.append(User.username.ilike(f"%{filters.username}%"))

        # Применяем условия к запросам
        if conditions:
            filter_condition = and_(*conditions)
            base_query = base_query.where(filter_condition)
            count_query = count_query.where(filter_condition)

    # Получаем общее количество записей
    total_result = await session.execute(count_query)
    total = total_result.scalar()

    # Получаем пагинированные результаты
    query = base_query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await session.execute(query)
    users = result.scalars().all()

    return users, total


async def create_user(session: AsyncSession, user: UserCreate):
    default_preferences = {
        "language": "ru",
        "dark_mode": False,
        "notifications": True,
        "timezone": "UTC+5",
    }

    user_data = user.model_dump()
    if not user_data.get("preferences"):
        user_data["preferences"] = default_preferences
    else:
        # Merge with defaults
        merged_preferences = {**default_preferences, **user_data["preferences"]}
        user_data["preferences"] = merged_preferences

    db_user = User(**user_data)
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


async def update_user_preferences(
    session: AsyncSession, telegram_id: int, preferences: PreferencesUpdate
):
    db_user = await get_user_by_telegram_id(session, telegram_id)
    if not db_user:
        return None

    current_preferences = db_user.preferences or {}
    new_preferences_dict = preferences.model_dump(exclude_unset=True)

    # Merge preferences
    updated_preferences = {**current_preferences, **new_preferences_dict}
    db_user.preferences = updated_preferences

    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_preference(
    session: AsyncSession, telegram_id: int, preference_key: str
):
    db_user = await get_user_by_telegram_id(session, telegram_id)
    if not db_user or not db_user.preferences:
        return None

    return db_user.preferences.get(preference_key)
