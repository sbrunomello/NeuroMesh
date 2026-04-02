from __future__ import annotations

from packages.contracts.commands import Command
from packages.contracts.events import Event


def plan_command(event: Event, default_target: str) -> Command | None:
    if event.type != "motion_detected":
        return None

    confidence = float(event.payload.get("confidence", 0))
    position = 120 if confidence >= 0.8 else 105
    target = event.payload.get("recommended_target", default_target)
    return Command(type="move_servo", target=target, payload={"position": position})
