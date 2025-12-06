from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum

from .base import BaseSchema, TimestampSchema, UserReferenceSchema

class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    file_name: str
    extension: str = Field(..., regex=r'^[a-zA-Z0-9]{1,10}$')
    size_bytes: int = Field(..., ge=0)

class DocumentCreate(DocumentBase):
    category_ids: List[UUID] = []
    status: DocumentStatus = DocumentStatus.DRAFT

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[DocumentStatus] = None
    category_ids: Optional[List[UUID]] = None

class DocumentInDB(DocumentBase, TimestampSchema, UserReferenceSchema):
    id: UUID
    status: DocumentStatus
    categories: List[Dict[str, Any]] = []

class DocumentResponse(DocumentInDB):
    chunk_count: int = 0
    has_embeddings: bool = False

class DocumentSearchQuery(BaseModel):
    query: str = Field(..., min_length=1)
    category_ids: Optional[List[UUID]] = None
    limit: int = Field(10, ge=1, le=100)
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)