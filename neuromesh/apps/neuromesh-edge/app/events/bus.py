from __future__ import annotations

import asyncio

from packages.contracts.events import Event


class EventBus:
    def __init__(self, on_subscribers_changed=None, on_drop=None) -> None:
        self._subscribers: set[asyncio.Queue[Event]] = set()
        self._on_subscribers_changed = on_subscribers_changed
        self._on_drop = on_drop

    def subscribe(self) -> asyncio.Queue[Event]:
        queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=200)
        self._subscribers.add(queue)
        if self._on_subscribers_changed:
            self._on_subscribers_changed(len(self._subscribers))
        return queue

    def unsubscribe(self, queue: asyncio.Queue[Event]) -> None:
        self._subscribers.discard(queue)
        if self._on_subscribers_changed:
            self._on_subscribers_changed(len(self._subscribers))

    async def publish(self, event: Event) -> None:
        stale: list[asyncio.Queue[Event]] = []
        for queue in self._subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                stale.append(queue)
                if self._on_drop:
                    self._on_drop()
        for queue in stale:
            self._subscribers.discard(queue)
        if stale and self._on_subscribers_changed:
            self._on_subscribers_changed(len(self._subscribers))
