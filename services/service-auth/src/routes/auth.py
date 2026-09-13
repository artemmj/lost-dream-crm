from fastapi import APIRouter, Depends

from src.services.auth import AuthService, get_auth_service
from src.schemas.auth import UserCreateRequest, AuthUser, LoginResponse, UserResponse
from src.dependencies.auth import get_current_user
from src.dependencies.user import get_user_service

from ..services.user import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    dto: UserCreateRequest, service: UserService = Depends(get_user_service)
):
    return await service.register_user(dto)


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: AuthUser, service: AuthService = Depends(get_auth_service)
):
    return await service.login(credentials)


@router.get("/logout")
async def logout(
    current_user: int = Depends(get_current_user),
    session_id: str = Depends(
        lambda: None
    ),  # Нужно передать session_id из токена или заголовка
    service: AuthService = Depends(get_auth_service),
):
    # В реальном проекте session_id лучше доставать из декодированного токена
    return await service.logout(current_user.id, session_id)


@router.get("/register_confirm")
async def confirm(token: str, service: AuthService = Depends(get_auth_service)):
    # Логика подтверждения через токен
    return {"message": "Confirmed"}
