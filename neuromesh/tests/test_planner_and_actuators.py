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


def test_actuator_resolution_and_rejection_cases():
    motion_mod = _load_module(
        Path(__file__).resolve().parents[1] / "apps" / "neuromesh-edge" / "app" / "modules" / "motion" / "actuator_service.py",
        "actuator_service",
    )
    actuators = {
        "servo_pan": {"position": 90, "min": 0, "max": 180},
        "servo_tilt": {"position": 90, "min": 15, "max": 165},
    }

    accepted = motion_mod.evaluate_command(actuators, "move_servo", "servo_pan", {"position": 190})
    assert accepted.accepted is True
    assert accepted.normalized_payload["position"] == 180

    invalid_target = motion_mod.evaluate_command(actuators, "move_servo", "servo_x", {"position": 90})
    assert invalid_target.accepted is False
    assert invalid_target.reason == "target_not_found"

    invalid_payload = motion_mod.evaluate_command(actuators, "move_servo", "servo_pan", {"position": "bad"})
    assert invalid_payload.accepted is False
    assert invalid_payload.reason.startswith("invalid_payload")
