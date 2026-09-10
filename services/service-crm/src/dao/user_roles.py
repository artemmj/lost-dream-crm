# dao/user_roles.py

from typing import Dict, List

from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload

from src.dao.base import BaseDAO
from src.models import User, Role
from src.dependencies.db_dependency import DBDependency


class UserRoleDAO(BaseDAO[Role]):
    model = Role

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def user_exists(self, user_id: int) -> bool:
        """Проверка существования пользователя"""
        async with self.db.read_only_scope() as session:
            stmt = select(exists().where(User.id == user_id))
            result = await session.execute(stmt)
            return result.scalar()

    async def roles_exist(self, role_ids: List[int]) -> Dict[int, bool]:
        """Массовая проверка существования ролей за один запрос"""
        if not role_ids:
            return {}
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(Role.id).where(Role.id.in_(role_ids))
            )
            existing_ids = set(result.scalars().all())
            return {role_id: role_id in existing_ids for role_id in role_ids}

    async def assign_roles(
        self, user_id: int, role_ids: List[int]
    ) -> List[Dict]:
        """
        Полная замена ролей пользователя.
        Возвращает обновлённый список ролей (список словарей).
        Бросает LookupError если юзер не найден.
        Бросает ValueError если какие-то role_ids не существуют.
        """
        async with self.db.session_scope() as session:
            # Загружаем пользователя
            result = await session.execute(
                select(User)
                .options(selectinload(User.roles))
                .where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise LookupError("User not found")

            # Загружаем роли
            if role_ids:
                roles_result = await session.execute(
                    select(Role).where(Role.id.in_(role_ids))
                )
                roles = list(roles_result.scalars().all())
                if len(roles) != len(role_ids):
                    raise ValueError("Some role IDs do not exist")
            else:
                roles = []

            # Назначаем
            user.roles = roles
            await session.flush()

            # Перечитываем с пермишенами для ответа
            refreshed_result = await session.execute(
                select(User)
                .options(selectinload(User.roles).selectinload(Role.permissions))
                .where(User.id == user_id)
            )
            refreshed_user = refreshed_result.scalar_one()

            return [
                {
                    "id": role.id,
                    "name": role.name,
                    "permissions": [
                        {
                            "id": perm.id,
                            "code": perm.code,
                            "description": perm.description,
                        }
                        for perm in role.permissions
                    ],
                }
                for role in refreshed_user.roles
            ]
