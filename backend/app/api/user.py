from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users - Пользователи"])

@router.get("/", response_model=None)
def list_users():
    """
    Список пользователей
    """
    return {"message": "Не реализовано"}