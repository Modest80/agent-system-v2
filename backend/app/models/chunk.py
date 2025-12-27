# app/models/chunk.py
from sqlalchemy import Column, Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from .base import BaseModel
from sqlalchemy import UniqueConstraint, Index

class Chunk(BaseModel):
    __tablename__ = 'chunks'
    
    document_id = Column(UUID(as_uuid=True), 
                       ForeignKey('documents.id', ondelete='CASCADE'), 
                       nullable=False,
                       index=True)
    chunk_index = Column(Integer, nullable=False, index=True)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    chunk_metadata = Column(JSONB, default=dict, nullable=True)
    
    # Связи
    document = relationship('Document', back_populates='chunks')
    
    # Ограничения
    

    __table_args__ = (
        CheckConstraint('chunk_index >= 0', name='chk_chunkindex_non_negative'),
        CheckConstraint('LENGTH(TRIM(text)) > 0', name='chk_text_not_empty'),
        CheckConstraint('LENGTH(text) <= 10000', name='chk_max_chunk_size'),
        UniqueConstraint('document_id', 'chunk_index', name='uq_chunks_document_chunk_index'),
        Index('ix_chunks_document_id_chunk_index', 'document_id', 'chunk_index'),
    )
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index})>"