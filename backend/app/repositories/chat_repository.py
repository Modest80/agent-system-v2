# Репозиторий для работы с чатами на базе ORM
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.chat import Chat
from app.models.message import Message
from app.schemas.message import MessageCreate


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db;
    
    # Операции с чатами
    def get_chat(self, id: str) -> Optional[Chat]:
        """Получение чата по ID с сообщениями"""
        return self.db.query(Chat).options(joinedload(Chat.messages)).filter(Chat.id == id).first()
    
    def get_chats_list(self, skip: int = 0, limit: int = 20) -> List[Chat]:
        """Получить список чатов"""
        pass
    
    def create_chat(self, title: str) -> Chat:
        """Создать новый чат"""
        pass
    
    def update_chat(self, id: str, new_title: str) -> Optional[Chat]:
        """Переименоватьч чат"""
        pass
    
    def delete_chat(self, id: str) -> bool:
        """Удалить чат"""
        pass
    
    # Операции с сообщениями
    def add_message(self, chat_id: str, message: MessageCreate) -> Message:
        """Добавление сообщения к чату"""
        pass

    def get_messages(self, id: str) -> List[Message]:
        """Получение сообщений чата"""
        pass
    
    def clear_messages(self, id: str) -> bool:
        """Удаление сообщений в чате"""
        pass
    
