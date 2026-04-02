import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest


class _Logger:
    def info_json(self, *_args, **_kwargs):
        return None

    def warning_json(self, *_args, **_kwargs):
        return None


@pytest.mark.asyncio
async def test_edge_core_client_flow(tmp_path: Path):
    edge_dir = Path(__file__).resolve().parents[1] / "apps" / "neuromesh-edge"
    core_dir = Path(__file__).resolve().parents[1] / "apps" / "neuromesh-core"

    port = 8123
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": "../..",
            "NEUROMESH_PORT": str(port),
            "NEUROMESH_DATA_DIR": str(tmp_path / "edge_data"),
        }
    )

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=edge_dir,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        deadline = time.time() + 10
        import httpx

        while time.time() < deadline:
            try:
                async with httpx.AsyncClient(timeout=1) as client:
                    res = await client.get(f"http://127.0.0.1:{port}/health")
                    if res.status_code == 200:
                        break
            except Exception:
                await asyncio.sleep(0.2)
        else:
            pytest.fail("edge did not start")

        os.environ["NEUROMESH_EDGE_HTTP_BASE"] = f"http://127.0.0.1:{port}"
        os.environ["NEUROMESH_EDGE_WS_URL"] = f"ws://127.0.0.1:{port}/events"

        if str(core_dir) not in sys.path:
            sys.path.insert(0, str(core_dir))

        from app.client.edge_client import EdgeClient
        from app.models.contracts import Command

        client = EdgeClient(_Logger())

        ack = await client.send_command(Command(type="move_servo", target="servo_pan", payload={"position": 130}))
        assert ack.accepted is True

        events: list[str] = []

        async def on_event(event):
            events.append(event.type)
            if len(events) >= 1:
                raise asyncio.CancelledError()

        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(client.consume_events(on_event), timeout=5)

        snapshot = await client.get_snapshot()
        assert snapshot["actuators"]["servo_pan"]["position"] == 130
        assert events
    finally:
        proc.terminate()
        proc.wait(timeout=5)
