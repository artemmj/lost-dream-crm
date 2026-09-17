from fastapi import Depends, HTTPException, status

from src.dependencies.auth import get_current_user
from src.schemas.user import UserMeResponse


class RequirePermission:
    """
    Зависимость проверки прав по коду пермишена (внутри service-auth).

    Используется роутами самого service-auth. Для других сервисов
    проверка доступна через GET /auth/introspect?permission=....
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
    """Короткая запись для проверки пермишенов: Depends(RequirePermission(code))."""
    return Depends(RequirePermission(code))
