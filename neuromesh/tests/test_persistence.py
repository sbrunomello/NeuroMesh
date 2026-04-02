import asyncio
import importlib.util
import json
from pathlib import Path

import pytest


class _Logger:
    def warning_json(self, *_args, **_kwargs):
        return None

    def error_json(self, *_args, **_kwargs):
        return None


def _load_persistence_writer():
    path = Path(__file__).resolve().parents[1] / "apps" / "neuromesh-edge" / "app" / "modules" / "bridge" / "persistence.py"
    spec = importlib.util.spec_from_file_location("persistence", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.PersistenceWriter


@pytest.mark.asyncio
async def test_persistence_writes_event_and_snapshot(tmp_path: Path):
    PersistenceWriter = _load_persistence_writer()
    writer = PersistenceWriter(str(tmp_path), _Logger())
    writer.start()

    enqueued = writer.enqueue_event({"type": "heartbeat", "payload": {"ok": True}})
    assert enqueued is True

    await asyncio.sleep(0.1)
    persisted_snapshot = await writer.persist_snapshot({"status": "running"})
    await writer.stop()

    assert persisted_snapshot is True
    events_file = tmp_path / "events.jsonl"
    snapshot_file = tmp_path / "snapshot.json"
    assert events_file.exists()
    assert snapshot_file.exists()

    line = events_file.read_text(encoding="utf-8").strip()
    assert json.loads(line)["type"] == "heartbeat"
    assert json.loads(snapshot_file.read_text(encoding="utf-8"))["status"] == "running"
