import asyncio
import logging

from src.dao.outbox_dao import OutboxDAO
from src.kafka.producer import kafka_producer
from src.settings import settings

logger = logging.getLogger(__name__)


class OutboxRelay:
    """Фоновая задача для публикации событий из outbox в Kafka"""

    def __init__(self, outbox_dao: OutboxDAO):
        self.outbox_dao = outbox_dao
        self._running = False
        self._task = None

    async def start(self):
        """Запуск relay"""
        await kafka_producer.start()
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("OutboxRelay started")

    async def _run_loop(self):
        """Основной цикл обработки"""
        while self._running:
            try:
                await self._process_batch()
            except Exception as e:
                logger.error(f"Outbox relay error: {e}", exc_info=True)

            await asyncio.sleep(settings.outbox_poll_interval_ms / 1000)

    async def _process_batch(self):
        """Обработка пакета событий"""
        events = await self.outbox_dao.get_unprocessed_batch(
            batch_size=settings.kafka.outbox_batch_size
        )

        if not events:
            return

        processed_ids = []
        for event in events:
            try:
                # Публикуем в Kafka
                topic = f"{event['aggregate_type']}.events.v1"
                await kafka_producer.send_event(
                    topic=topic,
                    key=str(event["aggregate_id"]),
                    event_type=event["event_type"],
                    payload=event["payload"],
                )
                processed_ids.append(event["id"])
            except Exception as e:
                logger.error(f"Failed to publish event {event['id']}: {e}")
                break  # Останавливаем batch для сохранения порядка

        # Помечаем обработанные
        if processed_ids:
            await self.outbox_dao.mark_processed(processed_ids)
            logger.info(f"Published {len(processed_ids)} events to Kafka")

    async def stop(self):
        """Остановка relay"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await kafka_producer.stop()
        logger.info("OutboxRelay stopped")
