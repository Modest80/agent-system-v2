# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool  # + NullPool
from contextvars import ContextVar
from typing import AsyncGenerator, Generator

from .core.config import settings

# sync - оставляем QueuePool
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    echo=settings.SQL_ECHO
)

async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.SQL_ECHO,
    pool_pre_ping=True,
    poolclass=NullPool,
    connect_args={"ssl": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

db_session: ContextVar[Session] = ContextVar("db_session")

def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# алиас для роутеров
get_async_session = get_async_db