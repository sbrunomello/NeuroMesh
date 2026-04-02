from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.modules.motion.calibration import ServoCalibration
from app.modules.motion.providers.base import MotionProvider


@dataclass
class ActuatorDecision:
    accepted: bool
    reason: str | None = None
    normalized_payload: dict[str, Any] | None = None


class ActuatorService:
    def __init__(self, provider: MotionProvider, calibration: dict[str, ServoCalibration]) -> None:
        self.provider = provider
        self.calibration = calibration

    def evaluate(self, command_type: str, target: str, payload: dict[str, Any]) -> ActuatorDecision:
        if command_type != "move_servo":
            return ActuatorDecision(accepted=False, reason="unsupported_type")

        calib = self.calibration.get(target)
        if calib is None:
            return ActuatorDecision(accepted=False, reason="target_not_found")

        requested = payload.get("position")
        if not isinstance(requested, int):
            return ActuatorDecision(accepted=False, reason="invalid_payload:position_must_be_int")

        normalized = normalize_servo_position(calib, requested)
        return ActuatorDecision(
            accepted=True,
            normalized_payload={
                "position": normalized,
                "requested": requested,
                "channel": calib.channel,
            },
        )

    def apply(self, target: str, normalized_payload: dict[str, Any]) -> None:
        channel = int(normalized_payload["channel"])
        angle = int(normalized_payload["position"])
        self.provider.move_servo(actuator=target, channel=channel, angle=angle)

    def health(self) -> dict[str, object]:
        return {
            "provider": self.provider.name,
            "servo_enabled": self.provider.name != "stub",
            "calibration_loaded": bool(self.calibration),
            "hardware": self.provider.health(),
        }


def normalize_servo_position(calib: ServoCalibration, requested: int) -> int:
    effective = requested + calib.offset_deg
    if calib.invert:
        effective = calib.max_angle - (effective - calib.min_angle)
    return max(calib.min_angle, min(calib.max_angle, effective))


def evaluate_command(actuators: dict[str, dict[str, int]], command_type: str, target: str, payload: dict[str, Any]) -> ActuatorDecision:
    # backward-compatible helper used by existing tests/routes when service isn't injected
    calibration = {
        name: ServoCalibration(
            channel=idx,
            min_angle=cfg.get("min", 0),
            max_angle=cfg.get("max", 180),
            home_angle=cfg.get("position", 90),
            offset_deg=0,
            invert=False,
        )
        for idx, (name, cfg) in enumerate(actuators.items())
    }
    service = ActuatorService(provider=_CompatProvider(actuators), calibration=calibration)
    return service.evaluate(command_type, target, payload)


class _CompatProvider(MotionProvider):
    name = "stub"

    def __init__(self, actuators: dict[str, dict[str, int]]) -> None:
        self._actuators = actuators

    def move_servo(self, *, actuator: str, channel: int, angle: int) -> None:
        self._actuators[actuator]["position"] = angle

    def health(self) -> dict[str, object]:
        return {"provider": self.name, "ready": True}
