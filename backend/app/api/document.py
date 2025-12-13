from app.models.document import Document

from fastapi import APIRouter

router = APIRouter(prefix="/documents")

@router.post("/upload", response_model=None)
def upload_document():
    """
    Загрузка документов в систему
    """
    return {"message": "Не реализовано"}


