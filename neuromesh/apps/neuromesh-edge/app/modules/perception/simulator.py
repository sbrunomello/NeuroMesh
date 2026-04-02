from __future__ import annotations

from app.modules.perception.providers.simulated import SimulatedPerceptionProvider

_provider = SimulatedPerceptionProvider()


def next_motion_state(current_moving: bool) -> tuple[bool, float, float]:
    moving, confidence, jitter, _meta = _provider.next_event(current_moving)
    return moving, confidence, jitter
