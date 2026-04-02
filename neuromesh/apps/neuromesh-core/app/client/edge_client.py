from __future__ import annotations

import asyncio

import httpx
from websockets.asyncio.client import connect
from websockets.exceptions import WebSocketException

from app.config import config
from app.models.contracts import Command, CommandAck, Event


class EdgeClient:
    def __init__(self, logger):
        self._logger = logger
        self._reconnect_attempt = 0

    async def send_command(self, command: Command) -> CommandAck:
        async with httpx.AsyncClient(base_url=config.edge_http_base, timeout=5) as client:
            response = await client.post("/commands", json=command.model_dump(mode="json"))
            response.raise_for_status()
            ack = CommandAck.model_validate(response.json())
            log_level = self._logger.info_json if ack.accepted else self._logger.warning_json
            log_level("command_ack", extra={"ack": ack.model_dump(mode="json")})
            return ack

    async def get_snapshot(self) -> dict:
        async with httpx.AsyncClient(base_url=config.edge_http_base, timeout=5) as client:
            response = await client.get("/snapshot")
            response.raise_for_status()
            return response.json()

    async def consume_events(self, on_event):
        while True:
            try:
                async with connect(config.edge_ws_url, ping_interval=20, ping_timeout=20) as ws:
                    self._reconnect_attempt = 0
                    self._logger.info_json("edge_ws_connected", extra={"url": config.edge_ws_url})
                    async for message in ws:
                        event = Event.model_validate_json(message)
                        self._logger.info_json("event_received", extra={"event": event.model_dump(mode='json')})
                        await on_event(event)
            except (OSError, WebSocketException, httpx.HTTPError) as exc:
                self._reconnect_attempt += 1
                self._logger.warning_json(
                    "edge_ws_reconnect",
                    extra={
                        "error": str(exc),
                        "delay_sec": config.reconnect_delay_sec,
                        "attempt": self._reconnect_attempt,
                    },
                )
                await asyncio.sleep(config.reconnect_delay_sec)
