from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from time import monotonic

from packages.contracts.commands import Command

from app.config import config
from app.events.bus import EventBus
from app.modules.bridge.persistence import PersistenceWriter
from app.modules.motion.actuator_service import ActuatorService
from app.modules.motion.calibration import load_or_default
from app.modules.motion.hardware.adapters import NoOpServoAdapter, PCA9685ServoAdapter
from app.modules.motion.providers.real_servo import RealServoMotionProvider
from app.modules.motion.providers.stub import StubMotionProvider
from app.modules.perception.service import PerceptionService
from app.modules.state.store import RuntimeState
from app.observability.logger import build_logger
from app.observability.metrics import RuntimeMetrics


@dataclass
class AppContext:
    bus: EventBus
    command_queue: asyncio.Queue[Command]
    state: RuntimeState
    logger: object
    metrics: RuntimeMetrics
    persistence: PersistenceWriter
    perception_service: PerceptionService
    actuator_service: ActuatorService


def build_context() -> AppContext:
    random.seed()
    logger = build_logger()
    metrics = RuntimeMetrics()
    calibration, calibration_loaded = load_or_default(config.actuators_config_path(), servo_enabled=config.servo.enabled)
    state = RuntimeState(node_id=config.node_id, start_time=monotonic(), calibration=calibration)
    state.status = "running"
    state.motion_runtime["calibration_loaded"] = calibration_loaded

    if config.servo.enabled and config.servo.provider == "pca9685":
        adapter = PCA9685ServoAdapter(
            i2c_bus=config.servo.i2c_bus,
            i2c_address=int(config.servo.i2c_address, 16),
            pwm_frequency=config.servo.pwm_frequency,
        )
        motion_provider = RealServoMotionProvider(adapter)
    else:
        motion_provider = StubMotionProvider()

    actuator_service = ActuatorService(provider=motion_provider, calibration=calibration)
    perception_service = PerceptionService.build(config.camera, logger)

    def _on_subscribers_changed(total: int) -> None:
        metrics.active_ws_subscribers = total

    def _on_drop() -> None:
        metrics.dropped_events += 1
        logger.warning_json("subscriber_dropped", extra={"dropped_events": metrics.dropped_events})

    bus = EventBus(on_subscribers_changed=_on_subscribers_changed, on_drop=_on_drop)
    persistence = PersistenceWriter(config.data_dir, logger)

    return AppContext(
        bus=bus,
        command_queue=asyncio.Queue(maxsize=200),
        state=state,
        logger=logger,
        metrics=metrics,
        persistence=persistence,
        perception_service=perception_service,
        actuator_service=actuator_service,
    )
