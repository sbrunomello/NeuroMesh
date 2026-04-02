from __future__ import annotations

import asyncio

from fastapi import FastAPI

from app.api.routes import build_router
from app.bootstrap import build_context
from app.bridge.runtime import handle_event
from app.config import config

ctx = build_context()
app = FastAPI(title="neuromesh-core")
app.include_router(build_router(ctx))


@app.on_event("startup")
async def startup() -> None:
    app.state.consumer_task = asyncio.create_task(ctx.edge_client.consume_events(lambda event: handle_event(ctx, event)))
    ctx.logger.info_json("core_started", extra={"edge_ws_url": config.edge_ws_url, "edge_http_base": config.edge_http_base})


@app.on_event("shutdown")
async def shutdown() -> None:
    task = app.state.consumer_task
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    ctx.logger.info_json("core_stopped")
