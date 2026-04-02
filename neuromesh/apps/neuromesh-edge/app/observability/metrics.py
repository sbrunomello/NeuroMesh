from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class RuntimeMetrics:
    events_published: int = 0
    events_persisted: int = 0
    commands_processed: int = 0
    commands_rejected: int = 0
    active_ws_subscribers: int = 0
    dropped_events: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)
