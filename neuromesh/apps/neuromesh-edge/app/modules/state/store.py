from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import Any

from packages.contracts.snapshot import Snapshot


@dataclass
class RuntimeState:
    node_id: str
    start_time: float
    status: str = "booting"
    sensors: dict[str, Any] = field(default_factory=lambda: {"pir_motion": False, "confidence": 0.0})
    actuators: dict[str, dict[str, int]] = field(
        default_factory=lambda: {
            "servo_pan": {"position": 90, "min": 0, "max": 180},
            "servo_tilt": {"position": 90, "min": 15, "max": 165},
        }
    )
    current_behavior: str = "idle"

    def uptime(self) -> float:
        return monotonic() - self.start_time

    def to_snapshot(self, metrics: dict[str, int]) -> Snapshot:
        return Snapshot(
            node_id=self.node_id,
            status=self.status,
            uptime=round(self.uptime(), 2),
            sensors=self.sensors,
            actuators=self.actuators,
            current_behavior=self.current_behavior,
            metrics=metrics,
        )
