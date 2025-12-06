from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    modified_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    created_by = Column(
        UUID(as_uuid=True),
        nullable=True
    )

    modified_by = Column(
        UUID(as_uuid=True),
        nullable=True
    )

    def to_dict(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }