from typing import List
from app.models.chat import Chat

from fastapi.responses import JSONResponse
from fastapi import APIRouter

router = APIRouter(prefix="/chats")

@router.get("/")
def get_chats():
    """
    Получить список чатов
    """
    return JSONResponse(
        status_code=405,
        content={"message": "Не реализовано"}
    )