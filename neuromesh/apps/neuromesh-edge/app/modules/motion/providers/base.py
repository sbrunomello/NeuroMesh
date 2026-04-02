from __future__ import annotations

from abc import ABC, abstractmethod


class MotionProvider(ABC):
    name: str

    @abstractmethod
    def move_servo(self, *, actuator: str, channel: int, angle: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> dict[str, object]:
        raise NotImplementedError
