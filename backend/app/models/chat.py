# app/models/chat.py
from sqlalchemy import Column, String, Boolean, Text
from .base import BaseModel

class Chat(BaseModel):
    __tablename__ = 'chats'
    
    title = Column(String(255), unique=False, nullable=False, index=True)

    def __repr__(self):
        return f"<Chat(id={self.id}, title={self.title}, created_at={self.created_at})>"