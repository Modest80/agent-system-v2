# create_tables.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models.base import Base
from app.models.user import User
from app.models.category import Category
from app.models.document import Document
from app.models.document_category import document_categories
from app.models.chunk import Chunk
from pgvector.sqlalchemy import Vector
from app.models.chat import Chat
from app.models.message import Message

print("Создание таблиц в правильном порядке...")

# Создаем таблицы в правильном порядке
Base.metadata.create_all(bind=engine, tables=[
    User.__table__,
    Category.__table__,
    Document.__table__,
    document_categories,
    Chunk.__table__,
    Chat.__table__,
    Message.__table__
])

print("Таблицы успешно созданы!")

# Проверка
from sqlalchemy import inspect
inspector = inspect(engine)
print("\nСозданные таблицы:")
for table_name in inspector.get_table_names():
    print(f"  - {table_name}")
    for column in inspector.get_columns(table_name):
        print(f"    {column['name']} ({column['type']})")