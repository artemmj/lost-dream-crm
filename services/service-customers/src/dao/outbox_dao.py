from typing import List, Dict, Any
from sqlalchemy import func, select, update
from src.dao.base import BaseDAO
from src.models.outbox_event import OutboxEvent


class OutboxDAO(BaseDAO[OutboxEvent]):
    model = OutboxEvent

    async def save_in_session(
        self,
        session,
        *,
        aggregate_type: str,
        aggregate_id: int,
        event_type: str,
        payload: dict,
    ) -> None:
        """Запись события ВНУТРИ существующей транзакции (атомарно с бизнес-операцией)"""
        event = OutboxEvent(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=payload,
        )
        session.add(event)
        await session.flush()

    async def get_unprocessed_batch(self, batch_size: int = 50) -> List[Dict[str, Any]]:
        """Получить пакет необработанных событий (read-only scope)"""
        async with self.db.read_only_scope() as session:
            result = await session.execute(
                select(self.model)
                .where(self.model.processed_at.is_(None))
                .order_by(self.model.created_at.asc())
                .limit(batch_size)
            )
            return [self._model_to_dict(e) for e in result.scalars().all()]

    async def mark_processed(self, event_ids: list) -> None:
        """Пометить события как обработанные"""
        async with self.db.session_scope() as session:
            await session.execute(
                update(self.model)
                .where(self.model.id.in_(event_ids))
                .values(processed_at=func.now())
            )
