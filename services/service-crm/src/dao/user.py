from typing import Dict, List, Optional, Tuple

from sqlalchemy import exists, select, func, or_
from sqlalchemy.orm import selectinload

from src.dao.base import BaseDAO
from src.models import User
from src.dependencies.db_dependency import DBDependency
from src.models.user import Role


class UserDAO(BaseDAO[User]):
    model = User

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def email_exists(self, email: str) -> bool:
        """Проверка существования email"""
        async with self.db.read_only_scope() as session:
            stmt = select(exists().where(User.email == email))
            result = await session.execute(stmt)
            return result.scalar()

    async def email_exists_excluding_user(
        self, email: str, exclude_user_id: int
    ) -> bool:
        """Проверка email, исключая конкретного пользователя"""
        async with self.db.read_only_scope() as session:
            stmt = select(
                exists().where(User.email == email, User.id != exclude_user_id)
            )
            result = await session.execute(stmt)
            return result.scalar()

    async def check_multiple_emails_exist(self, emails: List[str]) -> Dict[str, bool]:
        """Массовая проверка email за один запрос"""
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(User.email).where(User.email.in_(emails))
            )
            existing_emails = set(result.scalars().all())
            return {email: email in existing_emails for email in emails}

    async def get_by_email(self, email: str) -> Optional[Dict]:
        """Получение пользователя по email — возвращает словарь"""
        async with self.db.read_only_scope() as session:
            result = await session.execute(select(User).where(User.email == email))
            obj = result.scalar_one_or_none()
            if obj:
                return self._model_to_dict(obj)
            return None

    async def get_all_users(self) -> List[Dict]:
        async with self.db.read_only_scope() as session:
            result = await session.execute(select(User))
            objects = result.scalars().all()
            return [self._model_to_dict(obj) for obj in objects]

    async def get_obj_by_id(self, id: int) -> Optional[User]:
        async with self.db.session_scope() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()

    async def get_by_id_with_roles(self, user_id: int) -> Optional[Dict]:
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(self.model)
                .options(selectinload(self.model.roles).selectinload(Role.permissions))
                .where(self.model.id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return None

            return {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "is_banned": user.is_banned,
                "is_verified": user.is_verified,
                "roles": [
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
                    for role in user.roles
                ],
            }

    async def get_list_with_roles(
        self, page: int, per_page: int, search: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """Список пользователей с ролями и пермишенами — возвращает список словарей."""
        async with self.db.read_only_scope() as session:
            query = select(self.model).options(
                selectinload(self.model.roles).selectinload(Role.permissions)
            )
            count_query = select(func.count(self.model.id))

            if search:
                pattern = f"%{search}%"
                filter_cond = or_(
                    self.model.email.ilike(pattern),
                    self.model.first_name.ilike(pattern),
                    self.model.last_name.ilike(pattern),
                )
                query = query.where(filter_cond)
                count_query = count_query.where(filter_cond)

            total = (await session.execute(count_query)).scalar_one()

            result = await session.execute(
                query.order_by(self.model.id)
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            users = result.scalars().unique().all()

            items = [
                {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                    "is_banned": user.is_banned,
                    "is_verified": user.is_verified,
                    "roles": [
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
                        for role in user.roles
                    ],
                }
                for user in users
            ]

            return items, total
