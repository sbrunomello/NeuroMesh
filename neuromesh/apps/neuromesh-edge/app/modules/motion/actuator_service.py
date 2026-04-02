from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ActuatorDecision:
    accepted: bool
    reason: str | None = None
    normalized_payload: dict[str, Any] | None = None


def resolve_actuator(actuators: dict[str, dict[str, int]], target: str) -> dict[str, int] | None:
    return actuators.get(target)


def validate_move_servo_payload(payload: dict[str, Any]) -> tuple[int | None, str | None]:
    requested = payload.get("position")
    if not isinstance(requested, int):
        return None, "invalid_payload:position_must_be_int"
    return requested, None


def apply_servo_move(actuator: dict[str, int], requested: int) -> int:
    low, high = actuator["min"], actuator["max"]
    normalized = max(low, min(high, requested))
    actuator["position"] = normalized
    return normalized


def evaluate_command(actuators: dict[str, dict[str, int]], command_type: str, target: str, payload: dict[str, Any]) -> ActuatorDecision:
    if command_type != "move_servo":
        return ActuatorDecision(accepted=False, reason="unsupported_type")

    actuator = resolve_actuator(actuators, target)
    if actuator is None:
        return ActuatorDecision(accepted=False, reason="target_not_found")

    requested, error = validate_move_servo_payload(payload)
    if error:
        return ActuatorDecision(accepted=False, reason=error)

    normalized = apply_servo_move(actuator, requested)
    return ActuatorDecision(accepted=True, normalized_payload={"position": normalized, "requested": requested})
