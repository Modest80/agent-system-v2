from fastapi import APIRouter

router = APIRouter(prefix="/users")

@router.get("/", response_model=None)
def list_users():
    """
    Список пользователей
    """
    return {"message": "Не реализовано"}