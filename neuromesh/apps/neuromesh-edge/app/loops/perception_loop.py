from __future__ import annotations

import asyncio

from packages.contracts.events import Event


async def run_perception_loop(ctx, interval_sec: float) -> None:
    moving_state = False
    while True:
        try:
            moving_state, confidence, interval_jitter, metadata = ctx.perception_service.next_event(moving_state)
        except Exception as exc:
            ctx.logger.warning_json("perception_capture_failed", extra={"error": str(exc)})
            await asyncio.sleep(max(0.1, interval_sec))
            continue

        await asyncio.sleep(max(0.1, interval_sec + interval_jitter))

        ctx.state.sensors["pir_motion"] = moving_state
        ctx.state.sensors["confidence"] = confidence
        ctx.state.perception_runtime = ctx.perception_service.health()

        event = Event(
            type="motion_detected" if moving_state else "motion_cleared",
            source=ctx.state.node_id,
            payload={"sensor": "pir_motion", "confidence": confidence, **metadata},
        )

        await ctx.bus.publish(event)
        ctx.metrics.events_published += 1
        persisted = ctx.persistence.enqueue_event(event.model_dump(mode="json"))
        if persisted:
            ctx.metrics.events_persisted += 1
        ctx.logger.info_json("event_published", extra={"event": event.model_dump(mode="json"), "metrics": ctx.metrics.to_dict()})
