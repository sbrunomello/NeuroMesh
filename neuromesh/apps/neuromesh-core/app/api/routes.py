from fastapi import APIRouter


def build_router(ctx):
    router = APIRouter()

    @router.get("/health")
    async def health():
        return {"status": "ok", "component": "neuromesh-core"}

    @router.get("/edge/snapshot")
    async def edge_snapshot():
        return await ctx.edge_client.get_snapshot()

    return router
