# NeuroMesh Foundation (Hardened)

Base de runtime distribuído para robótica de baixo custo:
- `apps/neuromesh-edge` (Orange Pi)
- `apps/neuromesh-core` (Desktop)
- `packages/contracts` (contratos compartilhados)

## Build/Run rápido

### 1) Edge (Orange Pi)
```bash
cd neuromesh/apps/neuromesh-edge
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# ajuste NEUROMESH_NODE_ID/PORT/DATA_DIR conforme necessário
PYTHONPATH=../.. uvicorn app.main:app --host ${NEUROMESH_HOST:-0.0.0.0} --port ${NEUROMESH_PORT:-8000}
```

### 2) Core (Desktop Linux)
```bash
cd neuromesh/apps/neuromesh-core
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# ajuste NEUROMESH_EDGE_HTTP_BASE e NEUROMESH_EDGE_WS_URL para o IP do edge
PYTHONPATH=../.. uvicorn app.main:app --host ${NEUROMESH_HOST:-0.0.0.0} --port ${NEUROMESH_PORT:-8010}
```

### 3) Core (Desktop Windows PowerShell)
```powershell
cd neuromesh/apps/neuromesh-core
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edite .env com IP do edge
$env:PYTHONPATH="../.."
uvicorn app.main:app --host 0.0.0.0 --port 8010
```

## Validação manual

```bash
curl http://<EDGE_IP>:8000/health
curl http://<EDGE_IP>:8000/snapshot
curl -X POST http://<EDGE_IP>:8000/commands \
  -H 'Content-Type: application/json' \
  -d '{"type":"move_servo","target":"servo_tilt","payload":{"position":140}}'
```

WebSocket (`/events`):
```bash
python - <<'PY'
import asyncio, websockets
async def main():
    async with websockets.connect("ws://127.0.0.1:8000/events") as ws:
        for _ in range(5):
            print(await ws.recv())
asyncio.run(main())
PY
```

Persistência no edge (`NEUROMESH_DATA_DIR`):
- `events.jsonl`
- `snapshot.json`

## Limitações atuais da foundation

- Sem hardware real
- Sem pipeline de visão computacional real
- Sem mesh distribuída completa entre múltiplos nós
- Sem LLM
