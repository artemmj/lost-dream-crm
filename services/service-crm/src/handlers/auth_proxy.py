"""Прокси авторизации: валидация токена и проверка пермишенов через service-auth.

service-crm не декодирует JWT и не хранит сессии — все проверки делегируются
единому источнику аутентификации (service-auth) через GET /auth/introspect.
"""

import httpx

from src.settings import settings


class TokenInvalidError(Exception):
    """Токен отсутствует, невалиден или сессия истекла (401 от service-auth)."""


class PermissionDeniedError(Exception):
    """Недостаточно прав (403 от service-auth)."""


class AuthServiceUnavailableError(Exception):
    """service-auth недоступен или вернул неожиданную ошибку."""


class AuthProxy:
    """HTTP-клиент к service-auth для валидации токенов и пермишенов."""

    def __init__(self, base_url: str | None = None):
        self._base_url = (base_url or settings.auth_service_url).rstrip("/")

    async def introspect(
        self, authorization: str, permission: str | None = None
    ) -> dict:
        """
        Валидация токена (и опционально пермишена) через service-auth.

        Возвращает данные пользователя (UserMeResponse-совместимый dict)
        или бросает доменное исключение.
        """
        params = {"permission": permission} if permission else None
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url, timeout=5.0
            ) as client:
                response = await client.get(
                    "/introspect",
                    params=params,
                    headers={"Authorization": authorization},
                )
        except httpx.HTTPError as e:
            raise AuthServiceUnavailableError(f"Auth service unavailable: {e}") from e

        if response.status_code == 200:
            return response.json()
        if response.status_code == 401:
            raise TokenInvalidError(self._detail(response, "Token is invalid"))
        if response.status_code == 403:
            raise PermissionDeniedError(self._detail(response, "Permission denied"))
        raise AuthServiceUnavailableError(
            f"Auth service unexpected status: {response.status_code}"
        )

    async def get_current_user(self, authorization: str) -> dict:
        """Валидация токена без проверки пермишенов."""
        return await self.introspect(authorization=authorization)

    async def authorize(self, permission_code: str, authorization: str) -> dict:
        """Валидация токена + проверка пермишена по коду."""
        return await self.introspect(
            authorization=authorization, permission=permission_code
        )

    @staticmethod
    def _detail(response: httpx.Response, fallback: str) -> str:
        try:
            return str(response.json().get("detail", fallback))
        except Exception:
            return fallback
