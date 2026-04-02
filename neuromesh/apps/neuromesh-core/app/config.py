from __future__ import annotations

import os
from pydantic import BaseModel, Field


class CoreConfig(BaseModel):
    node_id: str = Field(default_factory=lambda: os.getenv("NEUROMESH_NODE_ID", "core-node-1"))
    component: str = Field(default_factory=lambda: os.getenv("NEUROMESH_COMPONENT", "core-runtime"))
    host: str = Field(default_factory=lambda: os.getenv("NEUROMESH_HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("NEUROMESH_PORT", "8010")))
    edge_http_base: str = Field(default_factory=lambda: os.getenv("NEUROMESH_EDGE_HTTP_BASE", "http://127.0.0.1:8000"))
    edge_ws_url: str = Field(default_factory=lambda: os.getenv("NEUROMESH_EDGE_WS_URL", "ws://127.0.0.1:8000/events"))
    reconnect_delay_sec: float = Field(default_factory=lambda: float(os.getenv("NEUROMESH_RECONNECT_DELAY_SEC", "2.0")))
    data_dir: str = Field(default_factory=lambda: os.getenv("NEUROMESH_DATA_DIR", "./data"))


def load_config() -> CoreConfig:
    return CoreConfig()


config = load_config()
