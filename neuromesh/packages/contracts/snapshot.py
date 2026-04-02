from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Snapshot(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    node_id: str = Field(min_length=1)
    status: str = Field(min_length=1)
    uptime: float = Field(ge=0)
    sensors: dict[str, Any] = Field(default_factory=dict)
    actuators: dict[str, Any] = Field(default_factory=dict)
    current_behavior: str = Field(min_length=1)
    metrics: dict[str, Any] = Field(default_factory=dict)
    perception: dict[str, Any] = Field(default_factory=dict)
    motion: dict[str, Any] = Field(default_factory=dict)
