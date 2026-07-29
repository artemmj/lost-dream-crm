import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, EmailStr, Field, StringConstraints


class AuthUser(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]
    first_name: str = Field(..., min_length=1, max_length=100, example="John")
    last_name: str = Field(..., min_length=1, max_length=100, example="Doe")


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
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


class LoginResponse(BaseModel):
    access_token: str

    model_config = {"from_attributes": True}


class UserMeResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    session_id: str | None = None
