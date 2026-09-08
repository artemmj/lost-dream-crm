from typing import Dict, List, Optional, Tuple

from sqlalchemy import exists, select, func, delete
from sqlalchemy.orm import selectinload

from src.dao.base import BaseDAO
from src.models import Role, Permission
from src.dependencies.db_dependency import DBDependency


class RoleDAO(BaseDAO[Role]):
    model = Role

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def get_list(
        self, page: int, per_page: int, search: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """Список ролей с пермишенами — возвращает список словарей"""
        async with self.db.read_only_scope() as session:
            query = select(self.model).options(selectinload(self.model.permissions))
            count_query = select(func.count(self.model.id))

            if search:
                pattern = f"%{search}%"
                query = query.where(self.model.name.ilike(pattern))
                count_query = count_query.where(self.model.name.ilike(pattern))

            total_result = await session.execute(count_query)
            total = total_result.scalar_one()

            result = await session.execute(
                query.order_by(self.model.name)
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            objects = result.scalars().unique().all()
            return [self._model_to_dict(obj) for obj in objects], total

    async def name_exists(
        self, name: str, exclude_role_id: Optional[int] = None
    ) -> bool:
        """Проверка существования роли по имени, опционально исключая конкретную"""
        async with self.db.read_only_scope() as session:
            conditions = [self.model.name == name]
            if exclude_role_id is not None:
                conditions.append(self.model.id != exclude_role_id)
            stmt = select(exists().where(*conditions))
            result = await session.execute(stmt)
            return result.scalar()

    async def get_permissions_by_ids(self, ids: List[int]) -> List[Permission]:
        """Получение ORM объектов пермишенов по списку ID (для назначения связям)"""
        if not ids:
            return []
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(Permission).where(Permission.id.in_(ids))
            )
            return list(result.scalars().all())

    async def create(
        self, name: str, permission_ids: Optional[List[int]] = None
    ) -> Dict:
        """Создание роли с пермишенами — возвращает словарь"""
        async with self.db.session_scope() as session:
            role = self.model(name=name)

            if permission_ids:
                perms = await self.get_permissions_by_ids(permission_ids)
                role.permissions = perms

            session.add(role)
            await session.flush()
            await session.refresh(role, attribute_names=["permissions"])
            return self._model_to_dict(role)

    async def update(
        self,
        role_id: int,
        name: Optional[str] = None,
        permission_ids: Optional[List[int]] = None,
    ) -> Optional[Dict]:
        """Обновление роли — возвращает словарь или None"""
        async with self.db.session_scope() as session:
            # Загружаем объект с пермишенами для корректного обновления M2M
            result = await session.execute(
                select(self.model)
                .options(selectinload(self.model.permissions))
                .where(self.model.id == role_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return None

            if name is not None:
                obj.name = name

            if permission_ids is not None:
                perms = await self.get_permissions_by_ids(permission_ids)
                obj.permissions = perms

            await session.flush()
            await session.refresh(obj, attribute_names=["permissions"])
            return self._model_to_dict(obj)

    async def delete_by_id(self, role_id: int) -> bool:
        """Удаление роли по ID"""
        async with self.db.session_scope() as session:
            result = await session.execute(
                delete(self.model).where(self.model.id == role_id)
            )
            return result.rowcount > 0

    async def get_obj_by_id(self, id: int) -> Optional[Role]:
        """Получение ORM объекта (для операций update/delete)"""
        async with self.db.session_scope() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
