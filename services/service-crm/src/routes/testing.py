from fastapi import APIRouter, Depends

from src.dependencies.permissions import RequirePermission
from src.schemas.user import UserMeResponse

router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/protected")
async def test_protected(
    current_user: UserMeResponse = Depends(RequirePermission("manage_roles")),
):
    """Требует авторизацию + конкретный пермишен 'manage_roles'."""
    return {
        "message": "Protected endpoint works",
        "required_permission": "manage_roles",
        "user_id": current_user.id,
        "email": current_user.email,
        "granted_via_roles": [
            role.name
            for role in current_user.roles
            if any(p.code == "manage_roles" for p in role.permissions)
        ],
    }


@router.get("/protected_2")
async def test_protected_2(
    current_user: UserMeResponse = Depends(RequirePermission("manage_roles")),
):
    """Требует авторизацию + конкретный пермишен 'manage_roles'."""
    return {
        "message": "Protected endpoint works",
        "required_permission": "manage_roles",
        "user_id": current_user.id,
        "email": current_user.email,
        "granted_via_roles": [
            role.name
            for role in current_user.roles
            if any(p.code == "manage_roles" for p in role.permissions)
        ],
    }
