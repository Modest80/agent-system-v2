# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, async_engine
from app.models.base import Base
from datetime import datetime

from app.api.router import api_router

VERSION = "0.2.1"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Запуск приложения...")
    
    # Создание таблиц (в продакшене используйте миграции)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    print("Завершение приложения...")
    await async_engine.dispose()

app = FastAPI(
    title="Agent System V2",
    version=VERSION,
    lifespan=lifespan,
    tags=["System"]
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем маршруты
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Agent System V2", "version": VERSION}

@app.get("/health")
async def health_check():    
    return {
        "status": "healthy",
        "date": datetime.now().strftime("%d.%m.%Y"),
        "time": datetime.now().strftime("%H:%M:%S"),
    }