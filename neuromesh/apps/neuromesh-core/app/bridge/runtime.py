from __future__ import annotations

from packages.contracts.events import Event

from app.planner.simple_planner import plan_command


async def handle_event(ctx, event: Event) -> None:
    command = plan_command(event, default_target="servo_pan")
    if command is None:
        return
    await ctx.edge_client.send_command(command)
