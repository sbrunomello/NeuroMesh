from __future__ import annotations

import os
from pydantic import BaseModel, Field


class EdgeConfig(BaseModel):
    node_id: str = Field(default_factory=lambda: os.getenv("NEUROMESH_NODE_ID", "edge-node-1"))
    component: str = Field(default_factory=lambda: os.getenv("NEUROMESH_COMPONENT", "edge-runtime"))
    host: str = Field(default_factory=lambda: os.getenv("NEUROMESH_HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("NEUROMESH_PORT", "8000")))
    perception_interval_sec: float = Field(default_factory=lambda: float(os.getenv("NEUROMESH_PERCEPTION_INTERVAL_SEC", "1.0")), ge=0.1)
    heartbeat_interval_sec: float = Field(default_factory=lambda: float(os.getenv("NEUROMESH_HEARTBEAT_INTERVAL_SEC", "2.0")), ge=0.1)
    data_dir: str = Field(default_factory=lambda: os.getenv("NEUROMESH_DATA_DIR", "./data"))


def load_config() -> EdgeConfig:
    return EdgeConfig()


config = load_config()
