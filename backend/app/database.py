from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextvars import ContextVar
from typing import AsyncGenerator, Generator
import os

from .core.config import settings

# Синхронный движок (для миграций и админских задач)
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    echo=settings.SQL_ECHO
)

# Асинхронный движок (для основного приложения)
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    echo=settings.SQL_ECHO
)

# Синхронная сессия
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)

# Асинхронная сессия
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Context var для хранения сессии в запросах
db_session: ContextVar[Session] = ContextVar('db_session')

def get_db() -> Generator[Session, None, None]:
    """Генератор синхронной сессии для зависимостей FastAPI"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Генератор асинхронной сессии для зависимостей FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()