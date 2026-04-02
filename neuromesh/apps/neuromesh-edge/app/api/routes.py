from fastapi import APIRouter

from packages.contracts.commands import Command, CommandAck

from app.modules.motion.actuator_service import evaluate_command


def build_router(ctx):
    router = APIRouter()

    @router.get("/health")
    async def health():
        return {"status": "ok", "node_id": ctx.state.node_id}

    @router.get("/snapshot")
    async def snapshot():
        return ctx.state.to_snapshot(ctx.metrics.to_dict()).model_dump(mode="json")

    @router.post("/commands", response_model=CommandAck)
    async def post_command(command: Command):
        preview = evaluate_command(ctx.state.actuators, command.type, command.target, command.payload)
        if not preview.accepted:
            ctx.metrics.commands_rejected += 1
            ack = CommandAck(
                accepted=False,
                command_id=command.command_id,
                target=command.target,
                normalized_payload={},
                reason=preview.reason,
            )
            ctx.logger.warning_json("command_rejected", extra={"command": command.model_dump(mode="json"), "reason": preview.reason})
            return ack

        if ctx.command_queue.full():
            ctx.metrics.commands_rejected += 1
            return CommandAck(accepted=False, command_id=command.command_id, target=command.target, normalized_payload={}, reason="queue_full")

        await ctx.command_queue.put(command)
        ack = CommandAck(
            accepted=True,
            command_id=command.command_id,
            target=command.target,
            normalized_payload=preview.normalized_payload or {},
            reason=None,
        )
        ctx.logger.info_json("command_received", extra={"command": command.model_dump(mode="json")})
        return ack

    return router
