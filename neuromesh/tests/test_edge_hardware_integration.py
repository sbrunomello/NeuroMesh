from pathlib import Path
import importlib
import os
import sys

EDGE_DIR = Path(__file__).resolve().parents[1] / "apps" / "neuromesh-edge"


def _import_edge(module: str):
    edge = str(EDGE_DIR)
    if edge in sys.path:
        sys.path.remove(edge)
    sys.path.insert(0, edge)
    for key in list(sys.modules.keys()):
        if key == "app" or key.startswith("app."):
            sys.modules.pop(key, None)
    return importlib.import_module(module)


def test_simulated_provider_emits_motion_tuple():
    mod = _import_edge("app.modules.perception.providers.simulated")
    provider = mod.SimulatedPerceptionProvider()
    moving, confidence, jitter, meta = provider.next_event(False)
    assert isinstance(moving, bool)
    assert 0.0 <= confidence <= 1.0
    assert isinstance(jitter, float)
    assert meta["source"] == "simulation"


def test_calibration_load_and_default(tmp_path: Path):
    mod = _import_edge("app.modules.motion.calibration")
    config_file = tmp_path / "actuators.json"
    config_file.write_text('{"servo_pan":{"channel":0,"min_angle":0,"max_angle":180,"home_angle":90,"offset_deg":0,"invert":false}}', encoding="utf-8")

    loaded, loaded_from_file = mod.load_or_default(config_file, servo_enabled=True)
    assert loaded_from_file is True
    assert loaded["servo_pan"].channel == 0

    defaults, loaded_from_file = mod.load_or_default(tmp_path / "missing.json", servo_enabled=False)
    assert loaded_from_file is False
    assert "servo_tilt" in defaults


def test_perception_service_fallback_when_camera_fails(monkeypatch):
    os.environ["NEUROMESH_CAMERA_ENABLED"] = "true"
    os.environ["NEUROMESH_CAMERA_SIMULATION_FALLBACK"] = "true"

    mod = _import_edge("app.modules.perception.service")
    config_mod = _import_edge("app.config")

    class _Logger:
        def info_json(self, *_args, **_kwargs):
            return None

        def warning_json(self, *_args, **_kwargs):
            return None

    monkeypatch.setattr(mod, "OpenCVMotionProvider", lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    service = mod.PerceptionService.build(config_mod.CameraConfig(), _Logger())
    assert service.provider.name == "simulated"


def test_snapshot_contains_new_fields():
    os.environ["NEUROMESH_SERVO_ENABLED"] = "false"
    mod = _import_edge("app.bootstrap")
    ctx = mod.build_context()
    snap = ctx.state.to_snapshot(ctx.metrics.to_dict()).model_dump(mode="json")
    assert "perception" in snap
    assert "motion" in snap
