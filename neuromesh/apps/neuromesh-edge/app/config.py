from __future__ import annotations

import os
from pathlib import Path
from pydantic import BaseModel, Field


class CameraConfig(BaseModel):
    enabled: bool = Field(default_factory=lambda: os.getenv("NEUROMESH_CAMERA_ENABLED", "false").lower() == "true")
    device: str = Field(default_factory=lambda: os.getenv("NEUROMESH_CAMERA_DEVICE", "0"))
    width: int = Field(default_factory=lambda: int(os.getenv("NEUROMESH_CAMERA_WIDTH", "640")), ge=64)
    height: int = Field(default_factory=lambda: int(os.getenv("NEUROMESH_CAMERA_HEIGHT", "480")), ge=64)
    fps: int = Field(default_factory=lambda: int(os.getenv("NEUROMESH_CAMERA_FPS", "15")), ge=1)
    mode: str = Field(default_factory=lambda: os.getenv("NEUROMESH_CAMERA_MODE", "motion"))
    simulation_fallback: bool = Field(
        default_factory=lambda: os.getenv("NEUROMESH_CAMERA_SIMULATION_FALLBACK", "true").lower() == "true"
    )


class ServoConfig(BaseModel):
    enabled: bool = Field(default_factory=lambda: os.getenv("NEUROMESH_SERVO_ENABLED", "false").lower() == "true")
    provider: str = Field(default_factory=lambda: os.getenv("NEUROMESH_SERVO_PROVIDER", "stub"))
    i2c_bus: int = Field(default_factory=lambda: int(os.getenv("NEUROMESH_SERVO_I2C_BUS", "1")), ge=0)
    i2c_address: str = Field(default_factory=lambda: os.getenv("NEUROMESH_SERVO_I2C_ADDRESS", "0x40"))
    pwm_frequency: int = Field(default_factory=lambda: int(os.getenv("NEUROMESH_SERVO_PWM_FREQUENCY", "50")), ge=1)
    actuators_config: str = Field(default_factory=lambda: os.getenv("NEUROMESH_ACTUATORS_CONFIG", "./config/actuators.json"))


class EdgeConfig(BaseModel):
    node_id: str = Field(default_factory=lambda: os.getenv("NEUROMESH_NODE_ID", "edge-node-1"))
    component: str = Field(default_factory=lambda: os.getenv("NEUROMESH_COMPONENT", "edge-runtime"))
    host: str = Field(default_factory=lambda: os.getenv("NEUROMESH_HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("NEUROMESH_PORT", "8000")))
    perception_interval_sec: float = Field(
        default_factory=lambda: float(os.getenv("NEUROMESH_PERCEPTION_INTERVAL_SEC", "1.0")), ge=0.1
    )
    heartbeat_interval_sec: float = Field(default_factory=lambda: float(os.getenv("NEUROMESH_HEARTBEAT_INTERVAL_SEC", "2.0")), ge=0.1)
    data_dir: str = Field(default_factory=lambda: os.getenv("NEUROMESH_DATA_DIR", "./data"))
    camera: CameraConfig = Field(default_factory=CameraConfig)
    servo: ServoConfig = Field(default_factory=ServoConfig)

    def actuators_config_path(self) -> Path:
        return Path(self.servo.actuators_config)


def load_config() -> EdgeConfig:
    return EdgeConfig()


config = load_config()
