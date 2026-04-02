from __future__ import annotations

from app.modules.motion.hardware.adapters import ServoHardwareAdapter
from app.modules.motion.providers.base import MotionProvider


class RealServoMotionProvider(MotionProvider):
    name = "pca9685"

    def __init__(self, adapter: ServoHardwareAdapter) -> None:
        self._adapter = adapter

    def move_servo(self, *, actuator: str, channel: int, angle: int) -> None:
        self._adapter.write_angle(channel=channel, angle=angle)

    def health(self) -> dict[str, object]:
        return {"provider": self.name, "hardware": self._adapter.health()}
