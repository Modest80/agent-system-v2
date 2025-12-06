# app/models/user.py
from sqlalchemy import Column, String, Boolean, Text
from .base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'
    
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Для аутентификации (если нужно)
    hashed_password = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"