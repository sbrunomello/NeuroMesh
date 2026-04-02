from __future__ import annotations

from abc import ABC, abstractmethod


class PerceptionProvider(ABC):
    name: str

    @abstractmethod
    def next_event(self, current_moving: bool) -> tuple[bool, float, float, dict[str, object]]:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> dict[str, object]:
        raise NotImplementedError

    def close(self) -> None:
        return None
