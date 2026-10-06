import asyncio

import pytest

from src.kafka.event_stream import EventStream


@pytest.mark.asyncio
async def test_event_stream_delivers_events_to_subscribers():
    stream = EventStream()
    received = []

    async def subscriber(event):
        received.append(event)

    unsubscribe = stream.subscribe(subscriber)
    stream.publish({"event_type": "customer.created.v1", "payload": {"customer_id": 1}})
    await asyncio.sleep(0)

    unsubscribe()
    assert received == [{"event_type": "customer.created.v1", "payload": {"customer_id": 1}}]


@pytest.mark.asyncio
async def test_event_stream_does_not_deliver_after_unsubscribe():
    stream = EventStream()
    received = []

    async def subscriber(event):
        received.append(event)

    unsubscribe = stream.subscribe(subscriber)
    unsubscribe()
    stream.publish({"event_type": "customer.created.v1", "payload": {"customer_id": 2}})
    await asyncio.sleep(0)

    assert received == []
