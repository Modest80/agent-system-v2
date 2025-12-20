from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from uuid import UUID
from datetime import datetime


class MessageCreate(BaseModel):
    role: Literal["user", "assistant", "system"] = "user"
    content: str = Field(min_length=1)
    meta: Optional[Dict[str, Any]] = None


class MessageOut(BaseModel):
    id: UUID
    chat_id: UUID
    role: str
    content: str
    meta: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}
