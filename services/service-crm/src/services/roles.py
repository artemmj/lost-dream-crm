from src.dao.roles_dao import RoleDAO
from src.models import Role


class RoleService:
    def __init__(self, role_dao: RoleDAO):
        self.dao = role_dao

    async def get_list(
        self, page: int, per_page: int, search: str | None = None
    ) -> tuple[list[Role], int]:
        return await self.dao.get_list(page, per_page, search)

    async def create(self, name: str, permission_ids: list[int] | None = None) -> Role:
        if await self.dao.exists_by_name(name):
            raise ValueError(f"Role '{name}' already exists")

        if permission_ids:
            perms = await self.dao.get_permissions_by_ids(permission_ids)
            if len(perms) != len(permission_ids):
                raise ValueError("Some permission IDs do not exist")

        return await self.dao.create(name, permission_ids)

    async def update(
        self,
        role_id: int,
        name: str | None = None,
        permission_ids: list[int] | None = None,
    ) -> Role:
        if name is not None and await self.dao.exists_by_name(name, exclude_id=role_id):
            raise ValueError(f"Role '{name}' already exists")

        if permission_ids is not None:
            perms = await self.dao.get_permissions_by_ids(permission_ids)
            if len(perms) != len(permission_ids):
                raise ValueError("Some permission IDs do not exist")

        role = await self.dao.update(role_id, name, permission_ids)
        if not role:
            raise LookupError("Role not found")
        return role

    async def delete(self, role_id: int) -> None:
        deleted = await self.dao.delete(role_id)
        if not deleted:
            raise LookupError("Role not found")
