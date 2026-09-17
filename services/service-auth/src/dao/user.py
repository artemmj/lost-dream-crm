from typing import Dict, Optional

from sqlalchemy import select, update, exists
from sqlalchemy.orm import selectinload

from src.dao.base import BaseDAO
from src.models.user import User, Role
from src.dependencies.db import DBDependency


class UserDAO(BaseDAO[User]):
    model = User

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def get_by_email(self, email: str) -> Optional[Dict]:
        """Получение пользователя по email — возвращает словарь (включая password_hash)."""
        async with self.db.read_only_scope() as session:
            result = await session.execute(select(User).where(User.email == email))
            obj = result.scalar_one_or_none()
            if obj:
                return self._model_to_dict(obj)
            return None

    async def get_by_id_with_roles(self, user_id: int) -> Optional[Dict]:
        """Получение пользователя с ролями и пермишенами — возвращает словарь."""
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(User)
                .options(selectinload(User.roles).selectinload(Role.permissions))
                .where(User.id == user_id)
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

    async def confirm_email(self, email: str) -> None:
        """Подтверждение email: активация и верификация пользователя."""
        async with self.db.session_scope() as session:
            stmt = (
                update(User)
                .where(User.email == email)
                .values(is_verified=True, is_active=True)
            )
            await session.execute(stmt)

    async def email_exists(self, email: str) -> bool:
        async with self.db.read_only_scope() as session:
            stmt = select(exists().where(User.email == email))
            result = await session.execute(stmt)
            return result.scalar()
