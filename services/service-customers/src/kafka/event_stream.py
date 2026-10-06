import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


Subscriber = Callable[[dict[str, Any]], Awaitable[None]]


class EventStream:
    """Быстрый in-memory stream для живой передачи Kafka-событий на фронтенд."""

    def __init__(self) -> None:
        self._subscribers: set[Subscriber] = set()

    def subscribe(self, subscriber: Subscriber):
        """Подписывает callback на новые события. Возвращает функцию отписки."""
        self._subscribers.add(subscriber)

        def unsubscribe() -> None:
            self._subscribers.discard(subscriber)

        return unsubscribe

    def publish(self, event: dict[str, Any]) -> None:
        """Публикует событие асинхронно всем подписчикам."""
        for subscriber in list(self._subscribers):
            asyncio.create_task(subscriber(event))

    def snapshot(self) -> list[dict[str, Any]]:
        """Возвращает пустой snapshot для совместимости с SSE-эндпоинтом."""
        return []


event_stream = EventStream()
