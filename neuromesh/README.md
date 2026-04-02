# NeuroMesh Foundation (Hardened)

Base de runtime distribuído para robótica de baixo custo:
- `apps/neuromesh-edge` (Orange Pi)
- `apps/neuromesh-core` (Desktop)
- `packages/contracts` (contratos compartilhados)

## O que o PR2 adiciona
- percepção real por câmera USB (OpenCV) com fallback para simulação
- providers plugáveis para percepção e motion
- caminho realista para servo por PCA9685/I2C com safety layer (clamp/offset/invert)
- calibração externa por arquivo JSON
- snapshot enriquecido com telemetria operacional

## Build/Run rápido

### 1) Edge (simulado)
```bash
cd neuromesh/apps/neuromesh-edge
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export NEUROMESH_CAMERA_ENABLED=false
export NEUROMESH_SERVO_ENABLED=false
PYTHONPATH=../.. uvicorn app.main:app --host ${NEUROMESH_HOST:-0.0.0.0} --port ${NEUROMESH_PORT:-8000}
```

### 2) Edge com câmera real
```bash
export NEUROMESH_CAMERA_ENABLED=true
export NEUROMESH_CAMERA_DEVICE=/dev/video0
export NEUROMESH_CAMERA_SIMULATION_FALLBACK=true
PYTHONPATH=../.. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3) Edge com servo stub/real
```bash
cp neuromesh/config/actuators.example.json neuromesh/config/actuators.json
export NEUROMESH_ACTUATORS_CONFIG=./config/actuators.json
export NEUROMESH_SERVO_ENABLED=false  # stub
# ou:
export NEUROMESH_SERVO_ENABLED=true
export NEUROMESH_SERVO_PROVIDER=pca9685
```

### 4) Core (Desktop Linux)
```bash
cd neuromesh/apps/neuromesh-core
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=../.. uvicorn app.main:app --host ${NEUROMESH_HOST:-0.0.0.0} --port ${NEUROMESH_PORT:-8010}
```

## Validação manual

```bash
curl http://<EDGE_IP>:8000/health
curl http://<EDGE_IP>:8000/snapshot
curl -X POST http://<EDGE_IP>:8000/commands \
  -H 'Content-Type: application/json' \
  -d '{"type":"move_servo","target":"servo_tilt","payload":{"position":140}}'
```

Persistência no edge (`NEUROMESH_DATA_DIR`):
- `events.jsonl`
- `snapshot.json`
