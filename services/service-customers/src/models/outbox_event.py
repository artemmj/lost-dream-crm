import uuid
from datetime import datetime

from sqlalchemy import String, BigInteger, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class OutboxEvent(Base):
    """
    Таблица Transactional Outbox.

    Гарантирует атомарную запись бизнес-события вместе с изменением данных.
    Фоновый relay читает необработанные записи и публикует их в Kafka.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    aggregate_type: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Тип агрегата, например 'customer'"
    )
    aggregate_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="ID бизнес-сущности"
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Тип события, например 'customer.created.v1'",
    )
    payload: Mapped[dict] = mapped_column(
        JSON, nullable=False, comment="Сериализованное тело события (без PII)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Время создания записи в outbox",
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Время успешной публикации в Kafka; NULL = не обработано",
    )

    def __repr__(self) -> str:
        return (
            f"OutboxEvent(id={self.id}, "
            f"type={self.event_type}, "
            f"aggregate={self.aggregate_type}:{self.aggregate_id})"
        )
