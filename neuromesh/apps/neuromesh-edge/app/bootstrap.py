from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from time import monotonic

from packages.contracts.commands import Command

from app.config import config
from app.events.bus import EventBus
from app.modules.bridge.persistence import PersistenceWriter
from app.modules.state.store import RuntimeState
from app.observability.logger import build_logger
from app.observability.metrics import RuntimeMetrics


@dataclass
class AppContext:
    bus: EventBus
    command_queue: asyncio.Queue[Command]
    state: RuntimeState
    logger: object
    metrics: RuntimeMetrics
    persistence: PersistenceWriter


def build_context() -> AppContext:
    random.seed()
    logger = build_logger()
    metrics = RuntimeMetrics()
    state = RuntimeState(node_id=config.node_id, start_time=monotonic())
    state.status = "running"

    def _on_subscribers_changed(total: int) -> None:
        metrics.active_ws_subscribers = total

    def _on_drop() -> None:
        metrics.dropped_events += 1
        logger.warning_json("subscriber_dropped", extra={"dropped_events": metrics.dropped_events})

    bus = EventBus(on_subscribers_changed=_on_subscribers_changed, on_drop=_on_drop)
    persistence = PersistenceWriter(config.data_dir, logger)

    return AppContext(
        bus=bus,
        command_queue=asyncio.Queue(maxsize=200),
        state=state,
        logger=logger,
        metrics=metrics,
        persistence=persistence,
    )
