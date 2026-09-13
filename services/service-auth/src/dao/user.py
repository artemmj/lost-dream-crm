from typing import Optional
from sqlalchemy import select, update, exists

from src.dao.base import BaseDAO
from src.models.user import User
from src.dependencies.db import DBDependency


class UserDAO(BaseDAO[User]):
    model = User

    def __init__(self, db: DBDependency):
        super().__init__(db)

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()

    async def confirm_email(self, email: str) -> None:
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
