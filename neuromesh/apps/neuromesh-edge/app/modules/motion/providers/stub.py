from __future__ import annotations

from app.modules.motion.providers.base import MotionProvider


class StubMotionProvider(MotionProvider):
    name = "stub"

    def __init__(self) -> None:
        self._last_move: dict[str, object] | None = None

    def move_servo(self, *, actuator: str, channel: int, angle: int) -> None:
        self._last_move = {"actuator": actuator, "channel": channel, "angle": angle}

    def health(self) -> dict[str, object]:
        return {"provider": self.name, "ready": True, "last_move": self._last_move}
