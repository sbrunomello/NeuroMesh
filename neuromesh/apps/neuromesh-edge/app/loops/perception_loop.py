from __future__ import annotations

import asyncio

from packages.contracts.events import Event

from app.modules.perception.simulator import next_motion_state


async def run_perception_loop(ctx, interval_sec: float) -> None:
    moving_state = False
    while True:
        moving_state, confidence, interval_jitter = next_motion_state(moving_state)
        await asyncio.sleep(max(0.1, interval_sec + interval_jitter))

        ctx.state.sensors["pir_motion"] = moving_state
        ctx.state.sensors["confidence"] = confidence
        event = Event(
            type="motion_detected" if moving_state else "motion_cleared",
            source=ctx.state.node_id,
            payload={"sensor": "pir_motion", "confidence": confidence},
        )

        await ctx.bus.publish(event)
        ctx.metrics.events_published += 1
        persisted = ctx.persistence.enqueue_event(event.model_dump(mode="json"))
        if persisted:
            ctx.metrics.events_persisted += 1
        ctx.logger.info_json("event_published", extra={"event": event.model_dump(mode="json"), "metrics": ctx.metrics.to_dict()})
