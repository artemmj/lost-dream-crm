import logging
from pathlib import Path
from typing import Optional

from aiokafka import AIOKafkaProducer

from src.settings import settings
from src.kafka.schema_registry import schema_registry_client

logger = logging.getLogger(__name__)


class KafkaProducerWithSchemaRegistry:
    """Асинхронный Kafka producer с поддержкой Schema Registry"""

    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None
        self.schemas_dir = Path(__file__).parent / "schemas"

    async def start(self):
        """Инициализация продюсера и регистрация схем"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka.kafka_bootstrap_servers,
            enable_idempotence=True,  # Гарантирует exactly-once в рамках сессии
            acks="all",
        )
        await self.producer.start()
        logger.info("Kafka producer started")

        # Регистрируем все схемы при старте
        await self._register_all_schemas()

    async def _register_all_schemas(self):
        """Регистрирует все .avsc файлы из каталога schemas/"""
        for schema_file in self.schemas_dir.glob("*.avsc"):
            subject = schema_file.stem  # customer_created -> subject
            try:
                await schema_registry_client.register_schema(subject, schema_file)
            except Exception as e:
                logger.error(f"Failed to register schema {subject}: {e}")
                raise

    async def send_event(
        self,
        topic: str,
        key: str,
        event_type: str,
        payload: dict,
    ) -> None:
        """
        Отправляет событие в Kafka с Avro-сериализацией.
        """
        if not self.producer:
            raise RuntimeError("Producer not started. Call start() first.")

        # ✅ Маппинг event_type → subject (имя файла схемы)
        # customer.created.v1 → customer_created
        # customer.updated.v1 → customer_updated
        subject = (
            event_type.split(".")[0] + "_" + event_type.split(".")[1]
        )  # customer_created

        logger.info(f"Looking up schema for subject: {subject}")

        schema = await schema_registry_client.get_schema(subject)
        schema_id = await schema_registry_client.get_schema_id(subject)

        # Сериализуем в Avro
        avro_bytes = schema_registry_client.serialize_avro(schema, payload)

        # Confluent Wire Format: magic byte + schema ID + data
        import struct

        wire_format = b"\x00" + struct.pack(">I", schema_id) + avro_bytes

        # Отправляем
        await self.producer.send_and_wait(
            topic=topic,
            key=key.encode("utf-8"),
            value=wire_format,
            headers=[("event_type", event_type.encode("utf-8"))],
        )

        logger.info(
            f"✅ Sent event {event_type} to topic {topic} (key={key}, schema_id={schema_id})"
        )

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
        await schema_registry_client.close()


# Синглтон
kafka_producer = KafkaProducerWithSchemaRegistry()
