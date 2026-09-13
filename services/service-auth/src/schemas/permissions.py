from pydantic import BaseModel, Field, ConfigDict


class PermissionCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-z][a-z0-9_:]*$")
    description: str | None = Field(None, max_length=255)


class PermissionUpdate(BaseModel):
    description: str | None = Field(None, max_length=255)
    # code намеренно не редактируем — это внутренний идентификатор


class PermissionRead(BaseModel):
    id: int
    code: str
    description: str | None
    model_config = ConfigDict(from_attributes=True)


class PermissionListResponse(BaseModel):
    items: list[PermissionRead]
    total: int
    page: int
    per_page: int


class PermissionBrief(BaseModel):
    id: int
    code: str
    description: str | None = None
    model_config = ConfigDict(from_attributes=True)
