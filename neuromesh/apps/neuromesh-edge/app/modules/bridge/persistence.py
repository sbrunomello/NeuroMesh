from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any


class PersistenceWriter:
    def __init__(self, data_dir: str, logger) -> None:
        self._base = Path(data_dir)
        self._logger = logger
        self._events_file = self._base / "events.jsonl"
        self._snapshot_file = self._base / "snapshot.json"
        self._event_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=1000)
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        self._base.mkdir(parents=True, exist_ok=True)
        self._task = asyncio.create_task(self._event_worker())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        await asyncio.gather(self._task, return_exceptions=True)

    def enqueue_event(self, event_payload: dict[str, Any]) -> bool:
        try:
            self._event_queue.put_nowait(event_payload)
            return True
        except asyncio.QueueFull:
            self._logger.warning_json("persistence_queue_full", extra={"file": str(self._events_file)})
            return False

    async def _event_worker(self) -> None:
        while True:
            event_payload = await self._event_queue.get()
            try:
                with self._events_file.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(event_payload, ensure_ascii=False) + "\n")
            except OSError as exc:
                self._logger.error_json("event_persist_failed", extra={"error": str(exc)})

    async def persist_snapshot(self, snapshot_payload: dict[str, Any]) -> bool:
        tmp = self._snapshot_file.with_suffix(".json.tmp")
        try:
            with tmp.open("w", encoding="utf-8") as handle:
                json.dump(snapshot_payload, handle, ensure_ascii=False)
            tmp.replace(self._snapshot_file)
            return True
        except OSError as exc:
            self._logger.error_json("snapshot_persist_failed", extra={"error": str(exc)})
            return False
