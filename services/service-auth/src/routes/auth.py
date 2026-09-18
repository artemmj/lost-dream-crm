from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.schemas.user import (
    AuthUser,
    LoginResponse,
    UserCreateRequest,
    UserResponse,
)
from src.schemas.user import UserMeResponse
from src.dependencies.auth import get_current_user
from src.dependencies.user import get_user_service
from src.services.user import UserService, UserAlreadyExistsError

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    dto: UserCreateRequest, service: UserService = Depends(get_user_service)
):
    """Регистрация нового пользователя."""
    try:
        return await service.register_user(dto)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: AuthUser, service: UserService = Depends(get_user_service)
):
    """Аутентификация: выпуск JWT и создание сессии в Redis."""
    return await service.login(user=credentials)


@router.get("/logout")
async def logout(
    current_user: UserMeResponse = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Выход: инвалидация сессии из токена."""
    return await service.logout_user(user=current_user)


@router.get("/register_confirm")
async def register_confirm(
    token: str, service: UserService = Depends(get_user_service)
):
    """Подтверждение email по токену из письма."""
    await service.confirm_user(token=token)
    return {"message": "Электронная почта подтверждена"}


@router.get("/introspect", response_model=UserMeResponse)
async def introspect(
    permission: str | None = Query(
        default=None, description="Код пермишена для проверки (опционально)"
    ),
    current_user: UserMeResponse = Depends(get_current_user),
):
    """
    Валидация токена и опциональная проверка пермишена.

    Единая точка авторизации для других сервисов (crm, commercial):
    - без permission — только валидация токена и сессии;
    - с permission — дополнительно проверка прав (is_superuser проходит всегда).
    """
    if permission is None:
        return current_user

    # Суперпользователь проходит любую проверку
    if current_user.is_superuser:
        return current_user

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    user_permissions: set[str] = set()
    for role in current_user.roles:
        for perm in role.permissions:
            user_permissions.add(perm.code)

    if permission not in user_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: '{permission}' required",
        )

    return current_user
