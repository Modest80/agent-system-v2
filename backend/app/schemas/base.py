from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class TimestampSchema:
    created_at: datetime
    modified_at: datetime

class UserReferenceSchema:
    created_by: UUID
    modified_by: UUID
    created_by_name: Optional[str] = None
    modified_by_name: Optional[str] = None