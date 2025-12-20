from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ChatCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ChatOut(BaseModel):
    id: UUID
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}