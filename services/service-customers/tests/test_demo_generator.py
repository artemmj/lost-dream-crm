import pytest

from src.kafka.demo_generator import demo_event_generator
from src.kafka.producer import kafka_producer


@pytest.mark.asyncio
async def test_demo_generator_sends_random_customer_event_with_auto_source(monkeypatch):
    calls = {}

    async def fake_send_event(topic, key, event_type, payload, source="manual"):
        calls["producer"] = {
            "topic": topic,
            "key": key,
            "event_type": event_type,
            "payload": payload,
            "source": source,
        }

    monkeypatch.setattr(kafka_producer, "send_event", fake_send_event)
    monkeypatch.setattr(demo_event_generator, "interval_seconds", 0.001)

    await demo_event_generator._publish_random_event()

    assert calls["producer"]["source"] == "auto"
    assert calls["producer"]["event_type"] in {"customer.created.v1", "customer.updated.v1"}
