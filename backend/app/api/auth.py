from fastapi import APIRouter

router = APIRouter(prefix="/auth")

@router.post("/", response_model=None)
def auth_user():
    """
    Авторизация пользователя
    """
    return {"message": "Не реализовано"}