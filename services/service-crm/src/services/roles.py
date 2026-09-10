# services/role_service.py

from typing import Optional

from src.dao.roles import RoleDAO


class RoleService:
    def __init__(self, role_dao: RoleDAO):
        self.dao = role_dao

    async def get_list(
        self, page: int, per_page: int, search: Optional[str] = None
    ) -> tuple[list[dict], int]:
        """Список ролей с пермишенами."""
        return await self.dao.get_list(page, per_page, search)

    async def get_by_id(self, role_id: int) -> Optional[dict]:
        """Получение роли по ID."""
        return await self.dao.get_by_id(role_id)

    async def create(self, name: str, permission_ids: Optional[list[int]] = None) -> dict:
        """Создание роли."""
        return await self.dao.create(name, permission_ids)

    async def update(
        self,
        role_id: int,
        name: Optional[str] = None,
        permission_ids: Optional[list[int]] = None,
    ) -> Optional[dict]:
        """Обновление роли."""
        return await self.dao.update(role_id, name, permission_ids)

    async def delete(self, role_id: int) -> None:
        """Удаление роли."""
        deleted = await self.dao.delete_by_id(role_id)
        if not deleted:
            raise LookupError("Role not found")
