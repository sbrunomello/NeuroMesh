from pathlib import Path
import importlib.util
import sys

from packages.contracts.events import Event


def _load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_planner_generates_command_for_motion_detected():
    planner_mod = _load_module(
        Path(__file__).resolve().parents[1] / "apps" / "neuromesh-core" / "app" / "planner" / "simple_planner.py",
        "simple_planner",
    )
    event = Event(type="motion_detected", source="edge", payload={"confidence": 0.9, "recommended_target": "servo_tilt"})
    cmd = planner_mod.plan_command(event, default_target="servo_pan")
    assert cmd is not None
    assert cmd.target == "servo_tilt"
    assert cmd.payload["position"] == 120


def test_servo_normalization_clamp_offset_and_invert():
    motion_mod = _load_module(
        Path(__file__).resolve().parents[1] / "apps" / "neuromesh-edge" / "app" / "modules" / "motion" / "actuator_service.py",
        "actuator_service",
    )
    calib_mod = _load_module(
        Path(__file__).resolve().parents[1] / "apps" / "neuromesh-edge" / "app" / "modules" / "motion" / "calibration.py",
        "calibration",
    )

    cfg = calib_mod.ServoCalibration(channel=0, min_angle=10, max_angle=170, home_angle=90, offset_deg=5, invert=False)
    assert motion_mod.normalize_servo_position(cfg, 0) == 10
    assert motion_mod.normalize_servo_position(cfg, 170) == 170

    inv = calib_mod.ServoCalibration(channel=0, min_angle=0, max_angle=180, home_angle=90, offset_deg=0, invert=True)
    assert motion_mod.normalize_servo_position(inv, 30) == 150


def test_actuator_service_with_stub_provider_accepts_and_rejects():
    motion_mod = _load_module(
        Path(__file__).resolve().parents[1] / "apps" / "neuromesh-edge" / "app" / "modules" / "motion" / "actuator_service.py",
        "actuator_service_stub",
    )
    calib_mod = _load_module(
        Path(__file__).resolve().parents[1] / "apps" / "neuromesh-edge" / "app" / "modules" / "motion" / "calibration.py",
        "calibration_stub",
    )
    provider_mod = _load_module(
        Path(__file__).resolve().parents[1] / "apps" / "neuromesh-edge" / "app" / "modules" / "motion" / "providers" / "stub.py",
        "motion_stub_provider",
    )

    service = motion_mod.ActuatorService(
        provider=provider_mod.StubMotionProvider(),
        calibration={"servo_pan": calib_mod.ServoCalibration(channel=0, min_angle=0, max_angle=180, home_angle=90, offset_deg=0, invert=False)},
    )

    accepted = service.evaluate("move_servo", "servo_pan", {"position": 181})
    assert accepted.accepted is True
    assert accepted.normalized_payload["position"] == 180

    rejected = service.evaluate("move_servo", "servo_x", {"position": 90})
    assert rejected.accepted is False
    assert rejected.reason == "target_not_found"
