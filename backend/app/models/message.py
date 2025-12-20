# app/models/message.py
from sqlalchemy import Column, String, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel

class Message(BaseModel):
    __tablename__ = "messages"

    chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # кто отправил
    role = Column(String(20), nullable=False)  # user | assistant | system

    # текст сообщения
    content = Column(Text, nullable=False)

    # сюда удобно класть "sources", "tokens", "model", "debug" и т.п.
    meta = Column(JSONB, nullable=True)

    chat = relationship("Chat", back_populates="messages")

    __table_args__ = (
        CheckConstraint("role IN ('user','assistant','system')", name="chk_message_role"),
        CheckConstraint("LENGTH(TRIM(content)) > 0", name="chk_message_content_not_empty"),
        Index("ix_messages_chat_id_created_at", "chat_id", "created_at"),
    )
