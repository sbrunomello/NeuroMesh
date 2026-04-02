from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from packages.contracts.commands import Command
from packages.contracts.events import Event
from packages.contracts.snapshot import Snapshot


def test_event_requires_non_empty_type():
    with pytest.raises(ValidationError):
        Event(type="", source="edge", payload={})


def test_command_requires_target_and_tz_timestamp():
    with pytest.raises(ValidationError):
        Command(type="move_servo", target="", payload={})

    with pytest.raises(ValidationError):
        Command(type="move_servo", target="servo_pan", payload={}, timestamp=datetime.now(timezone.utc).replace(tzinfo=None))


def test_snapshot_schema_version_and_metrics_present():
    snapshot = Snapshot(
        node_id="edge",
        status="running",
        uptime=0.5,
        sensors={},
        actuators={},
        current_behavior="idle",
        metrics={"events_published": 1},
    )
    assert snapshot.schema_version == "1.0"
    assert snapshot.metrics["events_published"] == 1
