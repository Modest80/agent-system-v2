from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # База данных
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = ""
    DATABASE_NAME: str = "agentsystemv2"
    
    # Embedding модель
    # EMBEDDING_MODEL: str = "text-embedding-ada-002"  # OpenAI
    # или: EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Sentence transformers
    
    # Размер чанков
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Настройки приложения
    PROJECT_NAM: str = "Agent System v.2"
    VERSION: str = "0.2.0"
    DEBUG: bool = True
    SQL_ECHO: bool = False
    
    # Пути для хранения файлов
    UPLOAD_DIR: str = "./uploads"
    PROCESSED_DIR: str = "./processed"
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()