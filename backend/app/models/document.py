# app/models/document.py
from sqlalchemy import Column, String, Text, BigInteger, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum as PyEnum
from .base import BaseModel

class DocumentStatus(PyEnum):
    DRAFT = "draft"
    PROCESSING = "processing"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class Document(BaseModel):
    __tablename__ = 'documents'
    
    title = Column(Text, nullable=False)
    file_name = Column(Text, nullable=False, index=True)
    extension = Column(String(20), nullable=False, index=True)
    size_bytes = Column(BigInteger, nullable=False)
    status = Column(String(50), nullable=False, default=DocumentStatus.DRAFT.value, index=True)
    
    # Связи
    categories = relationship(
        'Category',
        secondary='document_categories',
        back_populates='documents'
    )
    
    chunks = relationship(
        'Chunk',
        back_populates='document',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    # Ограничения
    __table_args__ = (
        CheckConstraint('size_bytes >= 0', name='chk_size_non_negative'),
        CheckConstraint(
            "status IN ('draft', 'processing', 'active', 'archived', 'deleted')",
            name='chk_valid_status'
        ),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, status={self.status})>"