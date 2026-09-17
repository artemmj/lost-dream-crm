from fastapi import APIRouter, Depends

from src.schemas.user import UserMeResponse
from src.dependencies.auth import get_current_user

router = APIRouter(tags=["Users"])


@router.get("/users/me", response_model=UserMeResponse)
async def me(
    current_user: UserMeResponse = Depends(get_current_user),
) -> UserMeResponse:
    """Профиль текущего пользователя по токену (для фронтенда)."""
    return current_user
