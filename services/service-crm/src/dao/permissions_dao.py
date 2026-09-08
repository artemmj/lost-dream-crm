from typing import Dict, List, Optional, Tuple

from sqlalchemy import exists, select, func, or_, delete

from src.dao.base import BaseDAO
from src.models import Permission
from src.dependencies.db_dependency import DBDependency


class PermissionDAO(BaseDAO[Permission]):
    model = Permission

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def get_list(
        self, page: int, per_page: int, search: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """Список пермишенов с пагинацией и поиском — возвращает список словарей"""
        async with self.db.read_only_scope() as session:
            query = select(self.model)
            count_query = select(func.count(self.model.id))

            if search:
                pattern = f"%{search}%"
                filter_cond = or_(
                    self.model.code.ilike(pattern),
                    self.model.description.ilike(pattern),
                )
                query = query.where(filter_cond)
                count_query = count_query.where(filter_cond)

            total_result = await session.execute(count_query)
            total = total_result.scalar_one()

            result = await session.execute(
                query.order_by(self.model.code)
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            objects = result.scalars().all()
            return [self._model_to_dict(obj) for obj in objects], total

    async def code_exists(self, code: str) -> bool:
        """Проверка существования пермишена по коду"""
        async with self.db.read_only_scope() as session:
            stmt = select(exists().where(self.model.code == code))
            result = await session.execute(stmt)
            return result.scalar()

    async def create(self, code: str, description: Optional[str] = None) -> Dict:
        """Создание пермишена — возвращает словарь"""
        async with self.db.session_scope() as session:
            perm = self.model(code=code, description=description)
            session.add(perm)
            await session.flush()
            await session.refresh(perm)
            return self._model_to_dict(perm)

    async def update_description(
        self, permission_id: int, description: Optional[str]
    ) -> Optional[Dict]:
        """Обновление описания — возвращает словарь или None"""
        async with self.db.session_scope() as session:
            obj = await self.get_obj_by_id(permission_id)
            if not obj:
                return None
            obj.description = description
            await session.flush()
            await session.refresh(obj)
            return self._model_to_dict(obj)

    async def delete_by_id(self, permission_id: int) -> bool:
        """Удаление пермишена по ID"""
        async with self.db.session_scope() as session:
            result = await session.execute(
                delete(self.model).where(self.model.id == permission_id)
            )
            return result.rowcount > 0

    async def get_obj_by_id(self, id: int) -> Optional[Permission]:
        """Получение ORM объекта (для операций update/delete)"""
        async with self.db.session_scope() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
