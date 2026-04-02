# neuromesh-edge

Runtime edge-first assíncrono para Orange Pi.

## Configuração

Copie `.env.example` e ajuste conforme o ambiente:

```bash
cp .env.example .env
```

Variáveis principais:
- `NEUROMESH_NODE_ID`
- `NEUROMESH_HOST`
- `NEUROMESH_PORT`
- `NEUROMESH_PERCEPTION_INTERVAL_SEC`
- `NEUROMESH_HEARTBEAT_INTERVAL_SEC`
- `NEUROMESH_DATA_DIR`

## Run (Orange Pi/Linux)

```bash
cd neuromesh/apps/neuromesh-edge
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export $(cat .env | xargs)  # opcional
PYTHONPATH=../.. uvicorn app.main:app --host ${NEUROMESH_HOST:-0.0.0.0} --port ${NEUROMESH_PORT:-8000}
```

## APIs

```bash
curl http://<EDGE_IP>:8000/health
curl http://<EDGE_IP>:8000/snapshot
curl -X POST http://<EDGE_IP>:8000/commands -H 'Content-Type: application/json' -d '{"type":"move_servo","target":"servo_pan","payload":{"position":120}}'
```

## WebSocket

```bash
python - <<'PY'
import asyncio, websockets
async def main():
    async with websockets.connect("ws://127.0.0.1:8000/events") as ws:
        for _ in range(3):
            print(await ws.recv())
asyncio.run(main())
PY
```

## Persistência

- `NEUROMESH_DATA_DIR/events.jsonl`: eventos append-only
- `NEUROMESH_DATA_DIR/snapshot.json`: último snapshot
