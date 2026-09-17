from typing import Annotated

from fastapi import Depends, HTTPException, status

from src.dependencies.auth_dependency import get_token_from_headers
from src.dependencies.db_dependency import db_dependency
from src.handlers.auth_proxy import (
    AuthProxy,
    TokenInvalidError,
    PermissionDeniedError,
    AuthServiceUnavailableError,
)
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

    Проверка делегируется service-auth (GET /auth/introspect?permission=...):
    там валидируется токен, сессия в Redis и наличие пермишена у ролей.

    Использование через Perm():
        current_user: UserMeResponse = Perm("list_permissions")

    Или напрямую:
        current_user: UserMeResponse = Depends(RequirePermission("list_permissions"))
    """

    def __init__(self, permission_code: str):
        self.permission_code = permission_code

    async def __call__(
        self,
        token: Annotated[str, Depends(get_token_from_headers)],
        auth_proxy: AuthProxy = Depends(AuthProxy),
    ) -> UserMeResponse:
        try:
            user_data = await auth_proxy.authorize(
                permission_code=self.permission_code, authorization=token
            )
        except TokenInvalidError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        except PermissionDeniedError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except AuthServiceUnavailableError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
            )

        return UserMeResponse(**user_data)


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
