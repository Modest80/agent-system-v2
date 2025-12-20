from typing import List
from app.models.chat import Chat
from app.services.chat_service import ChatService
from pydantic import BaseModel

from fastapi.responses import JSONResponse
from fastapi import APIRouter

router = APIRouter(prefix="/chats", tags=["Chats - Чаты"])

class ChatCreateRequest(BaseModel):
    title: str

@router.get("/")
def get_chats():
    """
    Получить список чатов
    """
    # Через сервис получить список чатов
    chatService = ChatService()
    chats = chatService.get_chats();
    # Вернуть список чатов клиенту
    return JSONResponse(
        status_code=200,
        content=chats
    )

@router.post("/")
def create_chat(data: ChatCreateRequest):
    """
    Создание чата
    """
    # Передать сервису создание чата
    # Созданный чат вернуть клиенту

    return JSONResponse(
        status_code=200,
        content={"title": data.title}
    )

@router.delete("/{id}")
def delete_chat(id: str):
    """
    Удаление чата
    """
    # Передать сервису id чата, который надо удалить
    # Вернуть клиенту результат удаления
    return JSONResponse(
        status_code=200,
        content={"message": f"Чат с {id} удалён!"}
    )

@router.get("/{id}")
def get_chat(id: str):
    """
    Получение чата
    """
    # Обратиться к сервису для получения данных чата
    # Вернуть клиенту чат с содержимым
    return JSONResponse(
        status_code=405,
        content={"message": "Не реализовано"}
    )

@router.put("/{id}")
def update_chat(newTitle: ChatCreateRequest):
    """
    Переименование чата
    """
    # Обратиться к сервису и передать id чата и новое имя
    # Вернуть клиенту результат переименования
    return JSONResponse(
        status_code=200,
        content={"message": "Чат переименован"}
    )