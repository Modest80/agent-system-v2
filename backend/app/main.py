# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, async_engine
from app.models.base import Base

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
    title="RAG System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "RAG System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}