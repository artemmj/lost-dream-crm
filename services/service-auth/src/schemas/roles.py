from pydantic import BaseModel, Field, ConfigDict

from src.schemas.permissions import PermissionBrief, PermissionRead


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    permission_ids: list[int] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=50)
    permission_ids: list[int] | None = None  # None = не менять, [] = убрать все


class RoleRead(BaseModel):
    id: int
    name: str
    permissions: list[PermissionRead] = []
    model_config = ConfigDict(from_attributes=True)


class RoleListResponse(BaseModel):
    items: list[RoleRead]
    total: int
    page: int
    per_page: int


class RoleBrief(BaseModel):
    id: int
    name: str
    permissions: list[PermissionBrief] = []
    model_config = ConfigDict(from_attributes=True)
