import asyncio
import logging
import random
import uuid
from datetime import UTC, datetime

from src.kafka.producer import kafka_producer
from src.settings import settings

logger = logging.getLogger(__name__)


class DemoEventGenerator:
    """Генерирует случайные customer-события в Kafka раз в секунду."""

    def __init__(self, interval_seconds: float = 1.0) -> None:
        self.interval_seconds = interval_seconds
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Запускает background-задачу генерации событий."""
        if self._task and not self._task.done():
            return

        self._task = asyncio.create_task(self._run())
        logger.info("DemoEventGenerator started")

    async def _run(self) -> None:
        """Публикует случайное событие с периодом interval_seconds."""
        try:
            while True:
                await asyncio.sleep(self.interval_seconds)
                await self._publish_random_event()
        except asyncio.CancelledError:
            logger.info("DemoEventGenerator stopped")
            raise

    def is_running(self) -> bool:
        """Возвращает состояние background-задачи."""
        return bool(self._task and not self._task.done())

    async def _publish_random_event(self) -> None:
        """Отправляет одно случайное demo-событие в Kafka."""
        event_type = random.choice(["customer.created.v1", "customer.updated.v1"])
        event_id = str(uuid.uuid4())

        payload = {
            "event_id": event_id,
            "customer_id": 999999,
        }
        if event_type == "customer.created.v1":
            payload["email_hash"] = "demo-auto-event-" + event_id[:8]
            payload["created_at"] = datetime.now(UTC).isoformat()
        else:
            payload["updated_at"] = datetime.now(UTC).isoformat()
            payload["changed_fields"] = ["first_name", "last_name", "status"]

        await kafka_producer.send_event(
            topic=settings.kafka.customer_events_topic,
            key="demo-customer-auto",
            event_type=event_type,
            payload=payload,
            source="auto",
        )

        logger.info("Generated demo event: %s", event_type)

    async def stop(self) -> None:
        """Останавливает background-задачу генерации событий."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None


demo_event_generator = DemoEventGenerator()
