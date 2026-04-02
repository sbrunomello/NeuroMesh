from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import Any

from packages.contracts.snapshot import Snapshot

from app.modules.motion.calibration import ServoCalibration


@dataclass
class RuntimeState:
    node_id: str
    start_time: float
    calibration: dict[str, ServoCalibration]
    status: str = "booting"
    sensors: dict[str, Any] = field(default_factory=lambda: {"pir_motion": False, "confidence": 0.0})
    actuators: dict[str, dict[str, int]] = field(default_factory=dict)
    current_behavior: str = "idle"
    perception_runtime: dict[str, Any] = field(default_factory=dict)
    motion_runtime: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.actuators:
            self.actuators = {
                name: {"position": cfg.home_angle, "min": cfg.min_angle, "max": cfg.max_angle, "channel": cfg.channel}
                for name, cfg in self.calibration.items()
            }

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
            perception=self.perception_runtime,
            motion=self.motion_runtime,
        )
