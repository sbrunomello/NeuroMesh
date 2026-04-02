from __future__ import annotations

import random

from app.modules.perception.providers.base import PerceptionProvider


class SimulatedPerceptionProvider(PerceptionProvider):
    name = "simulated"

    def __init__(self) -> None:
        self.frames_processed = 0

    def next_event(self, current_moving: bool) -> tuple[bool, float, float, dict[str, object]]:
        interval_jitter = random.uniform(-0.2, 0.3)
        moving = current_moving
        if random.random() < 0.35:
            moving = not moving
        confidence = round(random.uniform(0.5, 0.99) if moving else random.uniform(0.01, 0.4), 2)
        self.frames_processed += 1
        return moving, confidence, interval_jitter, {"source": "simulation", "frames_processed": self.frames_processed}

    def health(self) -> dict[str, object]:
        return {"provider": self.name, "camera_enabled": False, "frames_processed": self.frames_processed, "last_capture_ok": True}
