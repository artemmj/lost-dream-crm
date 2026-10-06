import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from src.kafka.event_stream import event_stream
from src.kafka.schema_registry import schema_registry_client
from src.settings import settings

logger = logging.getLogger(__name__)


def normalize_kafka_header(header: tuple[bytes | str, bytes | str]) -> str:
    """Нормализует значение Kafka header в строку независимо от типа значения."""
    key, value = header
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


class CustomerEventsConsumer:
    """Читает события из Kafka и публикует их в in-memory stream."""

    def __init__(self) -> None:
        self.consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        """Запускает Kafka consumer и background-обработчик."""
        self.consumer = AIOKafkaConsumer(
            settings.kafka.customer_events_topic,
            bootstrap_servers=settings.kafka.kafka_bootstrap_servers,
            group_id="customers-stream-demo",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await self.consumer.start()
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("CustomerEventsConsumer started")

    async def _run_loop(self) -> None:
        """Одновременно читает новый поток и публикует события."""
        if not self.consumer:
            return

        async for message in self.consumer:
            if not self._running:
                break

            logger.info("Consumer received message: topic=%s offset=%s", message.topic, message.offset)
            try:
                event = await self._deserialize_message(message)
                logger.info("Publishing event: type=%s offset=%s", event["event_type"], event["offset"])
                event_stream.publish(event)
                logger.info("Event published to stream: type=%s offset=%s", event["event_type"], event["offset"])
            except Exception as exc:
                logger.exception("Failed to process Kafka event: %s", exc)

    async def _deserialize_message(self, message) -> dict:
        """Десериализует Confluent Wire Format через Schema Registry."""
        if message.headers is None:
            raise ValueError("Kafka message has no headers")

        headers = {
            key.decode("utf-8") if isinstance(key, bytes) else str(key): normalize_kafka_header((key, value))
            for key, value in message.headers
        }
        event_type = headers.get("event_type")
        if not event_type:
            raise ValueError("Kafka message has no event_type header")

        payload = message.value
        if payload is None or len(payload) < 5 or payload[0] != 0:
            raise ValueError("Kafka message is not in Confluent Wire Format")

        schema_id = int.from_bytes(payload[1:5], byteorder="big", signed=False)
        avro_payload = payload[5:]
        schema = await schema_registry_client.get_schema_by_id(schema_id)

        import io

        import fastavro

        decoded = fastavro.schemaless_reader(io.BytesIO(avro_payload), schema)
        return {
            "event_type": event_type,
            "topic": message.topic,
            "partition": message.partition,
            "offset": message.offset,
            "timestamp": message.timestamp,
            "payload": decoded,
            "raw": json.loads(json.dumps(decoded, default=str)),
        }

    async def stop(self) -> None:
        """Останавливает consumer и отменяет background task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self.consumer:
            await self.consumer.stop()
            logger.info("CustomerEventsConsumer stopped")


customer_events_consumer = CustomerEventsConsumer()
