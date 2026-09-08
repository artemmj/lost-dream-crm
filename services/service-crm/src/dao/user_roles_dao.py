from typing import Dict, List, Optional

from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload

from src.dao.base import BaseDAO
from src.models import User, Role
from src.dependencies.db_dependency import DBDependency


class UserRoleDAO(BaseDAO[User]):
    model = User

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def user_exists(self, user_id: int) -> bool:
        """Проверка существования пользователя"""
        async with self.db.read_only_scope() as session:
            stmt = select(exists().where(self.model.id == user_id))
            result = await session.execute(stmt)
            return result.scalar()

    async def roles_exist(self, role_ids: List[int]) -> Dict[int, bool]:
        """Массовая проверка существования ролей за один запрос"""
        if not role_ids:
            return {}
        async with self.db.read_only_scope() as session:
            result = await session.execute(select(Role.id).where(Role.id.in_(role_ids)))
            existing_ids = set(result.scalars().all())
            return {role_id: role_id in existing_ids for role_id in role_ids}

    async def get_user_roles(self, user_id: int) -> Optional[List[Dict]]:
        """Получение ролей пользователя с пермишенами — возвращает список словарей или None"""
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(self.model)
                .options(selectinload(self.model.roles).selectinload(Role.permissions))
                .where(self.model.id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return None
            return [self._model_to_dict(role) for role in user.roles]

    async def assign_roles(
        self, user_id: int, role_ids: List[int]
    ) -> Optional[List[Dict]]:
        """
        Полная замена ролей пользователя.
        Возвращает обновлённый список ролей (список словарей) или None если юзер не найден.
        """
        async with self.db.session_scope() as session:
            result = await session.execute(
                select(self.model)
                .options(selectinload(self.model.roles))
                .where(self.model.id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return None

            if role_ids:
                roles_result = await session.execute(
                    select(Role).where(Role.id.in_(role_ids))
                )
                roles = list(roles_result.scalars().all())
            else:
                roles = []

            user.roles = roles
            await session.flush()

            # Перечитываем с пермишенами для ответа
            refreshed_result = await session.execute(
                select(self.model)
                .options(selectinload(self.model.roles).selectinload(Role.permissions))
                .where(self.model.id == user_id)
            )
            refreshed_user = refreshed_result.scalar_one()
            return [self._model_to_dict(role) for role in refreshed_user.roles]

    async def get_obj_by_id(self, id: int) -> Optional[User]:
        """Получение ORM объекта (для операций update/delete)"""
        async with self.db.session_scope() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
