from typing import Any, Generic, TypeVar, Type, Optional, List

from sqlalchemy import select, func

from src.models import Base
from src.dependencies.db_dependency import DBDependency

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model: Type[T]

    def __init__(self, db: DBDependency):
        self.db = db

    async def get_by_id(self, id: int) -> Optional[T]:
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(self.model).limit(limit).offset(offset)
            )
            return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> T:
        async with self.db.session_scope() as session:
            obj = self.model(**kwargs)
            session.add(obj)
            await session.flush()  # Получаем ID до коммита
            await session.refresh(obj)
            return obj

    async def update(self, obj: T) -> T:
        async with self.db.session_scope() as session:
            merged = await session.merge(obj)
            await session.flush()
            return merged

    async def delete(self, obj: T) -> None:
        async with self.db.session_scope() as session:
            await session.delete(obj)

    async def count(self) -> int:
        async with self.db.read_only_scope() as session:
            result = await session.execute(select(func.count()).select_from(self.model))
            return result.scalar_one()
