import pytest

from src.kafka.event_stream import event_stream
from src.kafka.producer import kafka_producer
from src.routes.demo import emit_demo_customer_event


@pytest.mark.asyncio
async def test_demo_created_event_is_published_only_through_kafka(monkeypatch):
    calls: dict[str, object] = {}

    async def fake_send_event(topic, key, event_type, payload, source="manual"):
        calls["producer"] = {
            "topic": topic,
            "key": key,
            "event_type": event_type,
            "payload": payload,
            "source": source,
        }

    def fake_publish(event):
        calls["stream"] = event

    monkeypatch.setattr(kafka_producer, "send_event", fake_send_event)
    monkeypatch.setattr(event_stream, "publish", fake_publish)

    response = await emit_demo_customer_event()

    assert response["accepted"] is True
    assert calls["producer"]["event_type"] == "customer.created.v1"
    assert "stream" not in calls
