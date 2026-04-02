from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError, model_validator


class ServoCalibration(BaseModel):
    channel: int = Field(ge=0)
    min_angle: int = Field(ge=0, le=180)
    max_angle: int = Field(ge=0, le=180)
    home_angle: int = Field(ge=0, le=180)
    offset_deg: int = Field(default=0, ge=-90, le=90)
    invert: bool = False

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.min_angle >= self.max_angle:
            raise ValueError("min_angle must be lower than max_angle")
        if not (self.min_angle <= self.home_angle <= self.max_angle):
            raise ValueError("home_angle must be between min_angle and max_angle")
        return self


def default_stub_calibration() -> dict[str, ServoCalibration]:
    return {
        "servo_pan": ServoCalibration(channel=0, min_angle=0, max_angle=180, home_angle=90, offset_deg=0, invert=False),
        "servo_tilt": ServoCalibration(channel=1, min_angle=15, max_angle=165, home_angle=90, offset_deg=0, invert=False),
    }


def load_calibration(path: Path) -> dict[str, ServoCalibration]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not raw:
        raise ValueError("actuators config must be a non-empty object")

    parsed: dict[str, ServoCalibration] = {}
    for name, servo_config in raw.items():
        if not isinstance(name, str) or not isinstance(servo_config, dict):
            raise ValueError("invalid servo calibration format")
        parsed[name] = ServoCalibration.model_validate(servo_config)
    return parsed


def load_or_default(path: Path, servo_enabled: bool) -> tuple[dict[str, ServoCalibration], bool]:
    if path.exists():
        return load_calibration(path), True
    if servo_enabled:
        raise FileNotFoundError(f"servo enabled but calibration file not found: {path}")
    return default_stub_calibration(), False
