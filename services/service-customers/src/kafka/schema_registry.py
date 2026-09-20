import json
import logging
from pathlib import Path
from typing import Dict

import httpx
import fastavro
from fastavro.schema import parse_schema

from src.settings import settings

logger = logging.getLogger(__name__)


class SchemaRegistryClient:
    """Асинхронный клиент Schema Registry"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=10.0)
        self._schema_cache: Dict[str, dict] = {}  # subject -> parsed schema

    async def register_schema(self, subject: str, schema_path: Path) -> int:
        """
        Регистрирует Avro-схему в Schema Registry.
        Возвращает schema ID.
        """
        with open(schema_path) as f:
            schema_json = json.load(f)

        # Проверяем валидность схемы локально
        parsed = parse_schema(schema_json)

        payload = {"schema": json.dumps(schema_json)}
        response = await self._client.post(
            f"{self.base_url}/subjects/{subject}/versions",
            json=payload,
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
        )

        if response.status_code == 409:
            # Схема уже зарегистрирована — получаем её ID
            logger.info(f"Schema {subject} already exists, fetching ID")
            return await self.get_schema_id(subject)

        response.raise_for_status()
        schema_id = response.json()["id"]
        logger.info(f"Registered schema {subject} with ID {schema_id}")

        # Кэшируем
        self._schema_cache[subject] = parsed
        return schema_id

    async def get_schema_id(self, subject: str) -> int:
        """Получить ID последней версии схемы для subject"""
        response = await self._client.get(
            f"{self.base_url}/subjects/{subject}/versions/latest"
        )
        response.raise_for_status()
        return response.json()["id"]

    async def get_schema(self, subject: str) -> dict:
        """Получить схему по subject (с кэшированием)"""
        if subject in self._schema_cache:
            return self._schema_cache[subject]

        response = await self._client.get(
            f"{self.base_url}/subjects/{subject}/versions/latest"
        )
        response.raise_for_status()
        schema_json = json.loads(response.json()["schema"])
        parsed = parse_schema(schema_json)
        self._schema_cache[subject] = parsed
        return parsed

    def serialize_avro(self, schema: dict, data: dict) -> bytes:
        """Сериализует данные в Avro-формат"""
        import io

        buffer = io.BytesIO()
        fastavro.schemaless_writer(buffer, schema, data)
        return buffer.getvalue()

    async def close(self):
        await self._client.aclose()


# Синглтон
schema_registry_client = SchemaRegistryClient(settings.kafka.schema_registry_url)
