from __future__ import annotations

from packages.contracts.events import Event


async def run_control_loop(ctx) -> None:
    while True:
        command = await ctx.command_queue.get()
        ctx.metrics.commands_processed += 1
        decision = ctx.actuator_service.evaluate(command.type, command.target, command.payload)

        if not decision.accepted:
            ctx.metrics.commands_rejected += 1
            ctx.logger.warning_json(
                "command_rejected",
                extra={
                    "reason": decision.reason,
                    "command": command.model_dump(mode="json"),
                    "metrics": ctx.metrics.to_dict(),
                },
            )
            continue

        normalized_payload = decision.normalized_payload or {}
        position = normalized_payload.get("position")
        ctx.state.current_behavior = "tracking" if position is not None and position != 90 else "idle"
        ctx.actuator_service.apply(command.target, normalized_payload)
        ctx.state.actuators[command.target]["position"] = int(position)
        ctx.state.motion_runtime = ctx.actuator_service.health()

        event = Event(
            type="servo_moved",
            source=ctx.state.node_id,
            payload={"actuator": command.target, **normalized_payload},
        )
        await ctx.bus.publish(event)
        ctx.metrics.events_published += 1
        persisted = ctx.persistence.enqueue_event(event.model_dump(mode="json"))
        if persisted:
            ctx.metrics.events_persisted += 1
        ctx.logger.info_json(
            "command_executed",
            extra={
                "command": command.model_dump(mode="json"),
                "normalized_payload": normalized_payload,
                "metrics": ctx.metrics.to_dict(),
            },
        )
