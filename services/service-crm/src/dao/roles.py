from typing import Dict, List, Optional, Tuple
from sqlalchemy import exists, select, func, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

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

            # 👇 Явная сериализация ВНУТРИ сессии
            items = [
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
                for role in objects
            ]

            return items, total

    async def get_by_id(self, role_id: int) -> Optional[Dict]:
        """Получение роли с пермишенами по ID — возвращает словарь"""
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(self.model)
                .options(selectinload(self.model.permissions))
                .where(self.model.id == role_id)
            )
            role = result.scalar_one_or_none()
            if not role:
                return None

            return {
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

    async def name_exists(
        self, name: str, exclude_role_id: Optional[int] = None
    ) -> bool:
        """Проверка существования роли по имени"""
        async with self.db.read_only_scope() as session:
            if exclude_role_id is not None:
                stmt = select(
                    exists().where(
                        self.model.name == name, self.model.id != exclude_role_id
                    )
                )
            else:
                stmt = select(exists().where(self.model.name == name))
            result = await session.execute(stmt)
            return result.scalar()

    async def get_permissions_by_ids(self, ids: List[int]) -> List[Permission]:
        """Получение ORM объектов пермишенов по списку ID"""
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
            # Проверка уникальности ВНУТРИ сессии
            stmt = select(exists().where(self.model.name == name))
            result = await session.execute(stmt)
            if result.scalar():
                raise ValueError(f"Role '{name}' already exists")

            role = self.model(name=name)

            if permission_ids:
                # Загружаем пермишены в той же сессии
                perms_result = await session.execute(
                    select(Permission).where(Permission.id.in_(permission_ids))
                )
                perms = list(perms_result.scalars().all())
                if len(perms) != len(permission_ids):
                    raise ValueError("Some permission IDs do not exist")
                role.permissions = perms

            session.add(role)
            try:
                await session.flush()
            except IntegrityError:
                raise ValueError(f"Role '{name}' already exists")

            # Перечитываем с пермишенами для ответа
            refreshed_result = await session.execute(
                select(self.model)
                .options(selectinload(self.model.permissions))
                .where(self.model.id == role.id)
            )
            refreshed_role = refreshed_result.scalar_one()

            return {
                "id": refreshed_role.id,
                "name": refreshed_role.name,
                "permissions": [
                    {
                        "id": perm.id,
                        "code": perm.code,
                        "description": perm.description,
                    }
                    for perm in refreshed_role.permissions
                ],
            }

    async def update(
        self,
        role_id: int,
        name: Optional[str] = None,
        permission_ids: Optional[List[int]] = None,
    ) -> Optional[Dict]:
        """Обновление роли — возвращает словарь или None"""
        async with self.db.session_scope() as session:
            result = await session.execute(
                select(self.model)
                .options(selectinload(self.model.permissions))
                .where(self.model.id == role_id)
            )
            role = result.scalar_one_or_none()
            if not role:
                return None

            if name is not None:
                # Проверка уникальности имени внутри сессии
                dup_stmt = select(
                    exists().where(self.model.name == name, self.model.id != role_id)
                )
                dup_result = await session.execute(dup_stmt)
                if dup_result.scalar():
                    raise ValueError(f"Role '{name}' already exists")
                role.name = name

            if permission_ids is not None:
                perms_result = await session.execute(
                    select(Permission).where(Permission.id.in_(permission_ids))
                )
                perms = list(perms_result.scalars().all())
                if len(perms) != len(permission_ids):
                    raise ValueError("Some permission IDs do not exist")
                role.permissions = perms

            try:
                await session.flush()
            except IntegrityError:
                raise ValueError("Role name already exists")

            # Перечитываем с пермишенами
            refreshed_result = await session.execute(
                select(self.model)
                .options(selectinload(self.model.permissions))
                .where(self.model.id == role_id)
            )
            refreshed_role = refreshed_result.scalar_one()

            return {
                "id": refreshed_role.id,
                "name": refreshed_role.name,
                "permissions": [
                    {
                        "id": perm.id,
                        "code": perm.code,
                        "description": perm.description,
                    }
                    for perm in refreshed_role.permissions
                ],
            }

    async def delete_by_id(self, role_id: int) -> bool:
        """Удаление роли по ID"""
        async with self.db.session_scope() as session:
            result = await session.execute(
                delete(self.model).where(self.model.id == role_id)
            )
            return result.rowcount > 0
