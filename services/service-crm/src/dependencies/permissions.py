from fastapi import Depends, HTTPException, status

from src.dependencies.auth_dependency import get_current_user
from src.dependencies.db_dependency import db_dependency
from src.dao.permissions import PermissionDAO
from src.dao.roles import RoleDAO
from src.dao.user_roles import UserRoleDAO
from src.services.permissions import PermissionService
from src.services.roles import RoleService
from src.services.user_role import UserRoleService
from src.schemas.user import UserMeResponse


def get_permission_service() -> PermissionService:
    """Фабрика сервиса пермишенов (db — модульный синглтон)"""
    return PermissionService(permission_dao=PermissionDAO(db_dependency))


def get_role_service() -> RoleService:
    """Фабрика сервиса ролей (db — модульный синглтон)"""
    return RoleService(role_dao=RoleDAO(db_dependency))


def get_user_role_service() -> UserRoleService:
    """Фабрика сервиса назначения ролей (db — модульный синглтон)"""
    return UserRoleService(user_role_dao=UserRoleDAO(db_dependency))


class RequirePermission:
    """
    Зависимость проверки прав по коду пермишена.

    Использование через Perm():
        current_user: UserMeResponse = Perm("list_permissions")

    Или напрямую:
        current_user: UserMeResponse = Depends(RequirePermission("list_permissions"))
    """

    def __init__(self, permission_code: str):
        self.permission_code = permission_code

    async def __call__(
        self,
        current_user: UserMeResponse = Depends(get_current_user),
    ) -> UserMeResponse:
        # Суперпользователь проходит любую проверку
        if getattr(current_user, "is_superuser", False):
            return current_user

        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Собираем коды пермишенов из уже загруженных ролей в /me/
        user_permissions: set[str] = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.add(perm.code)

        if self.permission_code not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: '{self.permission_code}' required",
            )

        return current_user


def Perm(code: str):
    """
    Короткая запись для проверки пермишенов.

    Использование:
        @router.get("/permissions")
        async def list_permissions(
            current_user: UserMeResponse = Perm("list_permissions"),
        ):
            ...

    Эквивалентно:
        current_user: UserMeResponse = Depends(RequirePermission("list_permissions"))
    """
    return Depends(RequirePermission(code))
