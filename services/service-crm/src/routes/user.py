from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field

from src.dependencies.db_dependency import DBDependency
from src.dao.user import UserDAO
from src.services.user import (
    UserService,
    UserCreateDTO,
    UserUpdateDTO,
    UserAlreadyExistsError,
    UserNotFoundError,
)

router = APIRouter(prefix="/users", tags=["Users"])


class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")
    password_hash: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100, example="John")
    last_name: str = Field(..., min_length=1, max_length=100, example="Doe")
    is_active: bool = Field(default=True)
    is_banned: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    is_verified: bool = Field(default=False)


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = Field(None, min_length=8)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    is_banned: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_banned: bool
    is_superuser: bool
    is_verified: bool

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int


class BulkCreateRequest(BaseModel):
    users: List[UserCreateRequest] = Field(..., min_items=1, max_items=100)


class BulkCreateResponse(BaseModel):
    created: int
    skipped: int
    skipped_emails: List[str]
    users: List[UserResponse]


class EmailCheckRequest(BaseModel):
    emails: List[EmailStr] = Field(..., min_items=1, max_items=50)


class EmailCheckResponse(BaseModel):
    emails: dict


def get_user_service(db: DBDependency = Depends()) -> UserService:
    """Фабрика сервиса с правильным графом зависимостей"""
    user_dao = UserDAO(db)
    return UserService(user_dao=user_dao)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Регистрация нового пользователя."""
    try:
        dto = UserCreateDTO(
            name=request.name,
            email=request.email,
            is_active=request.is_active,
        )
        return await user_service.register_user(dto)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """Получение пользователя по ID."""
    try:
        return await user_service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    user_service: UserService = Depends(get_user_service),
):
    """Список пользователей с пагинацией и фильтрацией."""
    users, total = await user_service.list_users(
        page=page,
        per_page=per_page,
        is_active=is_active,
    )
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Частичное обновление пользователя.
    Обновляются только переданные поля.
    """
    try:
        dto = UserUpdateDTO(
            name=request.name,
            email=request.email,
            is_active=request.is_active,
        )
        return await user_service.update_user(user_id, dto)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """Удаление пользователя."""
    try:
        await user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """Деактивация пользователя."""
    try:
        return await user_service.deactivate_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ===== Специализированные endpoints =====


@router.post("/check-emails", response_model=EmailCheckResponse)
async def check_emails(
    request: EmailCheckRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Проверка доступности email."""
    availability = await user_service.check_emails_availability(request.emails)
    return EmailCheckResponse(emails=availability)


@router.post(
    "/bulk", response_model=BulkCreateResponse, status_code=status.HTTP_201_CREATED
)
async def bulk_create_users(
    request: BulkCreateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Массовое создание пользователей."""
    dtos = [
        UserCreateDTO(name=u.name, email=u.email, is_active=u.is_active)
        for u in request.users
    ]
    result = await user_service.bulk_create_users(dtos)
    return result
