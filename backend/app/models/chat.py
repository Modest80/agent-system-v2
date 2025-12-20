# app/models/chat.py
from sqlalchemy import Column, String, Boolean, Text
from .base import BaseModel
from sqlalchemy.orm import relationship

class Chat(BaseModel):
    __tablename__ = 'chats'
    
    title = Column(String(255), unique=False, nullable=False, index=True)

    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    def __repr__(self):
        return f"<Chat(id={self.id}, title={self.title}, created_at={self.created_at})>"