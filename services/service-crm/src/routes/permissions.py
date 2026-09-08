# routers/perms.py
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.dependencies.permissions_dependency import (
    get_permission_service,
    get_role_service,
    get_user_role_service,
)
from src.services.permissions import PermissionService
from src.services.roles import RoleService
from src.services.user_role import UserRoleService
from src.schemas.user import (
    PermissionCreate,
    PermissionUpdate,
    PermissionRead,
    PermissionListResponse,
    RoleCreate,
    RoleUpdate,
    RoleRead,
    RoleListResponse,
    UserRoleAssign,
)

router = APIRouter(prefix="/perms", tags=["Permissions & Roles"])


# ===================== PERMISSIONS =====================


@router.get("/permissions", response_model=PermissionListResponse)
async def list_permissions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Поиск по code и description"),
    service: PermissionService = Depends(get_permission_service),
):
    items, total = await service.get_list(page, per_page, search)
    return PermissionListResponse(
        items=items, total=total, page=page, per_page=per_page
    )


@router.post(
    "/permissions", response_model=PermissionRead, status_code=status.HTTP_201_CREATED
)
async def create_permission(
    data: PermissionCreate,
    service: PermissionService = Depends(get_permission_service),
):
    try:
        perm = await service.create(data.code, data.description)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return perm


@router.patch("/permissions/{permission_id}", response_model=PermissionRead)
async def update_permission(
    permission_id: int,
    data: PermissionUpdate,
    service: PermissionService = Depends(get_permission_service),
):
    try:
        perm = await service.update_description(permission_id, data.description)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return perm


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int,
    service: PermissionService = Depends(get_permission_service),
):
    try:
        await service.delete(permission_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===================== ROLES =====================


@router.get("/roles", response_model=RoleListResponse)
async def list_roles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    service: RoleService = Depends(get_role_service),
):
    items, total = await service.get_list(page, per_page, search)
    return RoleListResponse(items=items, total=total, page=page, per_page=per_page)


@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    service: RoleService = Depends(get_role_service),
):
    try:
        role = await service.create(data.name, data.permission_ids)
    except ValueError as e:
        detail = str(e)
        code = 409 if "already exists" in detail else 400
        raise HTTPException(status_code=code, detail=detail)
    return role


@router.put("/roles/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    service: RoleService = Depends(get_role_service),
):
    try:
        role = await service.update(role_id, data.name, data.permission_ids)
    except ValueError as e:
        detail = str(e)
        code = 409 if "already exists" in detail else 400
        raise HTTPException(status_code=code, detail=detail)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
):
    try:
        await service.delete(role_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===================== USER ROLE ASSIGNMENT =====================


@router.get("/users/{user_id}/roles", response_model=list[RoleRead])
async def get_user_roles(
    user_id: int,
    service: UserRoleService = Depends(get_user_role_service),
):
    try:
        roles = await service.get_user_roles(user_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return roles


@router.put("/users/{user_id}/roles", response_model=list[RoleRead])
async def assign_user_roles(
    user_id: int,
    data: UserRoleAssign,
    service: UserRoleService = Depends(get_user_role_service),
):
    try:
        roles = await service.assign_roles(user_id, data.role_ids)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return roles
