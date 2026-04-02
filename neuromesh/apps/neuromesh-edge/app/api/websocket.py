from fastapi import APIRouter, WebSocket, WebSocketDisconnect


def build_websocket_router(ctx):
    router = APIRouter()

    @router.websocket("/events")
    async def events_stream(websocket: WebSocket):
        await websocket.accept()
        queue = ctx.bus.subscribe()
        ctx.logger.info_json("ws_connected", extra={"path": "/events", "active_ws_subscribers": ctx.metrics.active_ws_subscribers})
        try:
            while True:
                event = await queue.get()
                await websocket.send_json(event.model_dump(mode="json"))
        except WebSocketDisconnect:
            ctx.logger.info_json("ws_disconnected", extra={"path": "/events"})
        finally:
            ctx.bus.unsubscribe(queue)

    return router
