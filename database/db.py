import uuid
from typing import AsyncGenerator

from sqlalchemy import select, update, delete, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.settings import REAL_DATABASE_URL, DB_ECHO

async_engine = create_async_engine(REAL_DATABASE_URL, echo=DB_ECHO)

sync_engine = create_engine(REAL_DATABASE_URL.replace("asyncpg", "psycopg2"), echo=True)

async_session_factory = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    """Базовый класс декларативного подхода"""

    # pylint: disable = too-few-public-methods
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        """Представления"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs):
        obj = cls(**kwargs)
        session.add(obj)
        await session.flush()
        await session.commit()
        return obj

    @classmethod
    async def read_by_id(cls, session: AsyncSession, obj_id: uuid.UUID):
        result = await session.execute(select(cls).where(cls.id == obj_id))
        return result.unique().scalar_one_or_none()

    @classmethod
    async def update(cls, session: AsyncSession, id: uuid.UUID, **kwargs):
        stmt = update(cls).where(cls.id == id).values(**kwargs).returning(cls)
        obj = await session.execute(stmt)
        res = obj.scalar()
        if res:
            await session.commit()
            return res
        await session.rollback()
        return None

    @classmethod
    async def delete(cls, session: AsyncSession, obj_id: uuid.UUID):
        stmt = delete(cls).where(cls.id == obj_id).returning(cls)
        res = await session.execute(stmt)
        await session.commit()
        if res.scalar():
            return True
        return False


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """get session"""
    try:
        async with async_session_factory() as session:
            yield session
    finally:
        await session.close()
