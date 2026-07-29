from typing import Dict, List, Optional

from sqlalchemy import exists, select, update

from src.dao.base import BaseDAO
from src.models import User
from src.dependencies.db_dependency import DBDependency


class UserDAO(BaseDAO[User]):
    model = User

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def confirm(self, email: str) -> None:
        async with self.db.session_scope() as session:
            query = (
                update(self.model)
                .where(self.model.email == email)
                .values(is_verified=True, is_active=True)
            )
            await session.execute(query)
            await session.commit()

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

    async def get_active_users(self) -> List[Dict]:
        """Получение всех активных пользователей — возвращает список словарей"""
        async with self.db.read_only_scope() as session:
            result = await session.execute(select(User).where(User.is_active is True))
            objects = result.scalars().all()
            return [self._model_to_dict(obj) for obj in objects]

    async def deactivate_user(self, user_id: int) -> None:
        """Деактивация пользователя"""
        async with self.db.session_scope() as session:
            await session.execute(
                update(User).where(User.id == user_id).values(is_active=False)
            )

    async def activate_user(self, user_id: int) -> None:
        """Деактивация пользователя"""
        async with self.db.session_scope() as session:
            await session.execute(
                update(User).where(User.id == user_id).values(is_active=True)
            )

    # ЗАГОТОВКА: если нужен метод, возвращающий объект User (для update/delete)
    async def get_obj_by_id(self, id: int) -> Optional[User]:
        """Получение ORM объекта (для операций update/delete)"""
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
