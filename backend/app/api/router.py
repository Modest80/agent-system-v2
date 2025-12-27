from fastapi import APIRouter
from app.api import chat, document, user, auth, chunk

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(chat.router)
api_router.include_router(document.router)
api_router.include_router(chunk.router)
