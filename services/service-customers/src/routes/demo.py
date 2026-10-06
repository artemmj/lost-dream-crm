import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, status

from src.kafka.producer import kafka_producer
from src.settings import settings

router = APIRouter(prefix="/demo", tags=["Demo"])


@router.post("/customer-created", status_code=status.HTTP_202_ACCEPTED)
async def emit_demo_customer_event() -> dict:
    """Отправляет синтетическое customer.created.v1-событие в Kafka."""
    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "customer_id": 999999,
        "email_hash": "demo-event-" + event_id[:8],
        "created_at": datetime.now(UTC).isoformat(),
    }

    await kafka_producer.send_event(
        topic=settings.kafka.customer_events_topic,
        key="demo-customer",
        event_type="customer.created.v1",
        payload=payload,
    )

    return {"accepted": True, "event_type": "customer.created.v1", "event_id": event_id}


@router.post("/customer-updated", status_code=status.HTTP_202_ACCEPTED)
async def emit_demo_customer_updated_event() -> dict:
    """Отправляет синтетическое customer.updated.v1-событие в Kafka."""
    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "customer_id": 999999,
        "updated_at": datetime.now(UTC).isoformat(),
        "changed_fields": ["first_name", "last_name", "status"],
    }

    await kafka_producer.send_event(
        topic=settings.kafka.customer_events_topic,
        key="demo-customer",
        event_type="customer.updated.v1",
        payload=payload,
    )

    return {"accepted": True, "event_type": "customer.updated.v1", "event_id": event_id}
