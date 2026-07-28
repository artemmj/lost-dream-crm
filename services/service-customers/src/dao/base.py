from typing import Any, Generic, TypeVar, Type, Optional, List, Dict

from sqlalchemy import select, func

from src.models.base import Base
from src.dependencies.db_dependency import DBDependency

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model: Type[T]

    def __init__(self, db: DBDependency):
        self.db = db

    async def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Получение по ID — возвращает словарь"""
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            obj = result.scalar_one_or_none()
            if obj:
                return self._model_to_dict(obj)
            return None

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение всех — возвращает список словарей"""
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(self.model).limit(limit).offset(offset).order_by(self.model.id.desc())
            )
            objects = result.scalars().all()
            return [self._model_to_dict(obj) for obj in objects]

    async def create(self, **kwargs: Any) -> Dict[str, Any]:
        """Создание — возвращает словарь"""
        async with self.db.session_scope() as session:
            obj = self.model(**kwargs)
            session.add(obj)
            await session.flush()
            await session.refresh(obj)
            return self._model_to_dict(obj)

    async def update(self, obj: T) -> Dict[str, Any]:
        """Обновление — возвращает словарь"""
        async with self.db.session_scope() as session:
            merged = await session.merge(obj)
            await session.flush()
            await session.refresh(merged)
            return self._model_to_dict(merged)

    async def delete(self, obj: T) -> None:
        async with self.db.session_scope() as session:
            await session.delete(obj)

    async def count(self) -> int:
        async with self.db.read_only_scope() as session:
            result = await session.execute(select(func.count()).select_from(self.model))
            return result.scalar_one()

    def _model_to_dict(self, obj: T) -> Dict[str, Any]:
        """Конвертация модели в словарь (вызывается внутри сессии)"""
        return {
            column.key: getattr(obj, column.key)
            for column in self.model.__table__.columns
        }
