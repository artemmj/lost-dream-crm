import datetime
from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, Optional


class AuthUser(BaseModel):
    email: str
    password: Annotated[str, StringConstraints(min_length=2, max_length=128)]


class UserCreateRequest(BaseModel):
    email: str = Field(..., min_length=5)
    password: Annotated[str, StringConstraints(min_length=4, max_length=128)]
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str


class UserMeResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_superuser: bool
    session_id: Optional[str] = None
