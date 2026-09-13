import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field, StringConstraints

from src.schemas.roles import RoleBrief


class AuthUser(BaseModel):
    email: str
    password: Annotated[str, StringConstraints(min_length=2, max_length=128)]


class UserCreateRequest(BaseModel):
    email: str = Field(..., min_length=5, example="john@example.com")
    password: Annotated[str, StringConstraints(min_length=4, max_length=128)]
    first_name: str = Field(..., min_length=1, max_length=100, example="John")
    last_name: str = Field(..., min_length=1, max_length=100, example="Doe")


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    # password_hash: Optional[str] = Field(None, min_length=8)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    is_banned: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    email: str
    password_hash: str
    first_name: str
    last_name: str
    is_active: bool
    is_banned: bool
    is_superuser: bool
    is_verified: bool
    roles: list[RoleBrief] = []

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int


class LoginResponse(BaseModel):
    access_token: str

    model_config = {"from_attributes": True}


class UserMeResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_banned: bool
    is_superuser: bool
    is_verified: bool
    session_id: str | None = None
    roles: list[RoleBrief] = []


class UserListWithRolesResponse(BaseModel):
    users: list[UserMeResponse]
    total: int
    page: int
    per_page: int


class UserRoleAssign(BaseModel):
    role_ids: list[int] = Field(
        ..., description="Полный список ID ролей для пользователя"
    )
