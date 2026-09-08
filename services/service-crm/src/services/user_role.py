from src.dao.user_roles import UserRoleDAO
from src.models import Role


class UserRoleService:
    def __init__(self, user_role_dao: UserRoleDAO):
        self.dao = user_role_dao

    async def get_user_roles(self, user_id: int) -> list[Role]:
        roles = await self.dao.get_user_roles(user_id)
        if roles is None:
            raise LookupError("User not found")
        return roles

    async def assign_roles(self, user_id: int, role_ids: list[int]) -> list[Role]:
        roles, error = await self.dao.assign_roles(user_id, role_ids)
        if error:
            raise ValueError(error) if "role" in error.lower() else LookupError(error)
        return roles
