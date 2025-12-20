# Сервис для работы с чатами
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.chat_repository import ChatRepository

class ChatService:
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo

    def create_chat(self, title: str):
        # Создание чата
        pass

    def get_chats(self):
        # Получение списка чатов
        return []

    def get_chat_by_id(self, id: str):
        # Получение чата по UUID
        pass

    def update_chat(self, id: str, newTitle: str):
        # Переименование чата
        pass