from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth - Авторизация"])

@router.post("/", response_model=None)
def auth_user():
    """
    Авторизация пользователя
    """
    return {"message": "Не реализовано"}