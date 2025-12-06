# app/models/document_category.py
from sqlalchemy import Column, ForeignKey, Table, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

document_categories = Table(
    'document_categories',
    Base.metadata,
    Column('document_id', UUID(as_uuid=True), 
           ForeignKey('documents.id', ondelete='CASCADE'), 
           primary_key=True),
    Column('category_id', UUID(as_uuid=True), 
           ForeignKey('categories.id', ondelete='CASCADE'), 
           primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column('modified_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
    Column('created_by', UUID(as_uuid=True), nullable=True),
    Column('modified_by', UUID(as_uuid=True), nullable=True)
)