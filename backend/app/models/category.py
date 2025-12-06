# app/models/category.py
from sqlalchemy import Column, Text, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel

class Category(BaseModel):
    __tablename__ = 'categories'
    
    name = Column(Text, nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    
    # Связи
    parent = relationship('Category', remote_side='Category.id', backref='children')
    
    # Связь с документами через промежуточную таблицу
    documents = relationship(
        'Document',
        secondary='document_categories',
        back_populates='categories'
    )
    
    __table_args__ = (
        UniqueConstraint('name', 'parent_id', name='uniq_category_name_per_parent'),
        CheckConstraint('parent_id IS NULL OR parent_id != id', name='chk_not_self_parent'),
    )
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, parent_id={self.parent_id})>"