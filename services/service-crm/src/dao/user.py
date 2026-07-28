from typing import Dict, List, Optional

from sqlalchemy import exists, select, update

from src.dao.base import BaseDAO
from src.models import User
from src.dependencies.db_dependency import DBDependency


class UserDAO(BaseDAO[User]):
    model = User

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def email_exists(self, email: str) -> bool:
        async with self.db.read_only_scope() as session:
            stmt = select(exists().where(User.email == email))
            result = await session.execute(stmt)
            return result.scalar()

    async def email_exists_excluding_user(
        self, email: str, exclude_user_id: int
    ) -> bool:
        async with self.db.read_only_scope() as session:
            stmt = select(
                exists().where(User.email == email, User.id != exclude_user_id)
            )
            result = await session.execute(stmt)
            return result.scalar()

    async def check_multiple_emails_exist(self, emails: List[str]) -> Dict[str, bool]:
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(User.email).where(User.email.in_(emails))
            )
            existing_emails = set(result.scalars().all())
            return {email: email in existing_emails for email in emails}

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self.db.read_only_scope() as session:
            result = await session.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()

    async def get_active_users(self) -> List[User]:
        async with self.db.read_only_scope() as session:
            result = await session.execute(select(User).where(User.is_active == True))
            return list(result.scalars().all())

    async def deactivate_user(self, user_id: int) -> None:
        async with self.db.session_scope() as session:
            await session.execute(
                update(User).where(User.id == user_id).values(is_active=False)
            )
            # Коммит произойдёт автоматически при выходе из контекста

    async def find_by_email_pattern(self, pattern: str) -> List[User]:
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(User).where(User.email.ilike(f"%{pattern}%"))
            )
            return list(result.scalars().all())

    async def bulk_activate_users(self, user_ids: List[int]) -> None:
        async with self.db.session_scope() as session:
            await session.execute(
                update(User).where(User.id.in_(user_ids)).values(is_active=True)
            )

    async def get_user_with_orders(self, user_id: int) -> Optional[User]:
        async with self.db.read_only_scope() as session:
            from sqlalchemy.orm import joinedload

            result = await session.execute(
                select(User)
                .options(joinedload(User.orders))  # если есть relationship
                .where(User.id == user_id)
            )
            return result.unique().scalar_one_or_none()
