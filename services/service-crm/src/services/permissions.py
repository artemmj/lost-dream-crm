from src.dao.permissions_dao import PermissionDAO
from src.models import Permission


class PermissionService:
    def __init__(self, permission_dao: PermissionDAO):
        self.dao = permission_dao

    async def get_list(
        self, page: int, per_page: int, search: str | None = None
    ) -> tuple[list[Permission], int]:
        return await self.dao.get_list(page, per_page, search)

    async def create(self, code: str, description: str | None) -> Permission:
        if await self.dao.exists_by_code(code):
            raise ValueError(f"Permission '{code}' already exists")
        return await self.dao.create(code, description)

    async def update_description(
        self, permission_id: int, description: str | None
    ) -> Permission:
        perm = await self.dao.update_description(permission_id, description)
        if not perm:
            raise LookupError("Permission not found")
        return perm

    async def delete(self, permission_id: int) -> None:
        deleted = await self.dao.delete(permission_id)
        if not deleted:
            raise LookupError("Permission not found")
