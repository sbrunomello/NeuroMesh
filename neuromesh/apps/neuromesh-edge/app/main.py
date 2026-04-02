from __future__ import annotations

import asyncio

from fastapi import FastAPI

from app.api.routes import build_router
from app.api.websocket import build_websocket_router
from app.bootstrap import build_context
from app.config import config
from app.loops.control_loop import run_control_loop
from app.loops.heartbeat_loop import run_heartbeat_loop
from app.loops.perception_loop import run_perception_loop

ctx = build_context()
app = FastAPI(title="neuromesh-edge")
app.include_router(build_router(ctx))
app.include_router(build_websocket_router(ctx))


@app.on_event("startup")
async def startup() -> None:
    ctx.persistence.start()
    app.state.tasks = [
        asyncio.create_task(run_perception_loop(ctx, config.perception_interval_sec)),
        asyncio.create_task(run_control_loop(ctx)),
        asyncio.create_task(run_heartbeat_loop(ctx, config.heartbeat_interval_sec)),
    ]
    ctx.logger.info_json("edge_started", extra={"node_id": ctx.state.node_id, "data_dir": config.data_dir})


@app.on_event("shutdown")
async def shutdown() -> None:
    for task in app.state.tasks:
        task.cancel()
    await asyncio.gather(*app.state.tasks, return_exceptions=True)
    await ctx.persistence.stop()
    ctx.logger.info_json("edge_stopped")
