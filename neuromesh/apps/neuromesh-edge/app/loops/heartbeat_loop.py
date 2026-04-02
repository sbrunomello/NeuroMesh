from __future__ import annotations

import asyncio

from packages.contracts.events import Event


async def run_heartbeat_loop(ctx, interval_sec: float) -> None:
    while True:
        await asyncio.sleep(interval_sec)
        snapshot = ctx.state.to_snapshot(ctx.metrics.to_dict())
        event = Event(
            type="heartbeat",
            source=ctx.state.node_id,
            payload={"status": snapshot.status, "uptime": snapshot.uptime, "metrics": snapshot.metrics},
        )
        await ctx.bus.publish(event)
        ctx.metrics.events_published += 1
        persisted_event = ctx.persistence.enqueue_event(event.model_dump(mode="json"))
        if persisted_event:
            ctx.metrics.events_persisted += 1
        await ctx.persistence.persist_snapshot(snapshot.model_dump(mode="json"))
        ctx.logger.info_json("heartbeat", extra={"uptime": snapshot.uptime, "metrics": ctx.metrics.to_dict()})
