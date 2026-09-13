from src.dao.user_roles import UserRoleDAO


class UserRoleService:
    def __init__(self, user_role_dao: UserRoleDAO):
        self.dao = user_role_dao

    async def assign_roles(self, user_id: int, role_ids: list[int]) -> list[dict]:
        """
        Полная замена ролей пользователя.
        Исключения пробрасываются из DAO напрямую.
        """
        return await self.dao.assign_roles(user_id, role_ids)
