from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


EMBEDDING_DIM = 1536


class ChunkBase(BaseModel):
    chunk_index: int = Field(ge=0)
    text: str = Field(min_length=1, max_length=10000)
    chunk_metadata: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None

    @field_validator("embedding")
    @classmethod
    def validate_embedding(cls, v):
        if v is None:
            return v
        if len(v) != EMBEDDING_DIM:
            raise ValueError(f"embedding must have length {EMBEDDING_DIM}")
        return v


class ChunkCreate(ChunkBase):
    pass


class ChunkBulkCreate(BaseModel):
    chunks: List[ChunkCreate]


class ChunkRead(ChunkBase):
    id: UUID
    document_id: UUID

    class Config:
        from_attributes = True


class ChunkMetadataUpdate(BaseModel):
    chunk_metadata: Dict[str, Any]


class ChunkSearchRequest(BaseModel):
    embedding: List[float]
    top_k: int = Field(default=5, ge=1, le=50)
    document_id: Optional[UUID] = None

    @field_validator("embedding")
    @classmethod
    def validate_embedding(cls, v):
        if len(v) != EMBEDDING_DIM:
            raise ValueError(f"embedding must have length {EMBEDDING_DIM}")
        return v


class ChunkSearchHit(BaseModel):
    chunk: ChunkRead
    distance: float


class ChunkSearchResponse(BaseModel):
    hits: List[ChunkSearchHit]
