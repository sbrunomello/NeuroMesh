# neuromesh-edge

Runtime edge-first assíncrono para Orange Pi com providers plugáveis de percepção e motion.

## Configuração principal

### Câmera/percepção
- `NEUROMESH_CAMERA_ENABLED=true|false`
- `NEUROMESH_CAMERA_DEVICE=/dev/video1` (ou `0`, `1`)
- `NEUROMESH_CAMERA_WIDTH=640`
- `NEUROMESH_CAMERA_HEIGHT=480`
- `NEUROMESH_CAMERA_FPS=15`
- `NEUROMESH_CAMERA_MODE=motion`
- `NEUROMESH_CAMERA_SIMULATION_FALLBACK=true|false`

### Servo/motion
- `NEUROMESH_SERVO_ENABLED=true|false`
- `NEUROMESH_SERVO_PROVIDER=stub|pca9685`
- `NEUROMESH_SERVO_I2C_BUS=1`
- `NEUROMESH_SERVO_I2C_ADDRESS=0x40`
- `NEUROMESH_SERVO_PWM_FREQUENCY=50`
- `NEUROMESH_ACTUATORS_CONFIG=./config/actuators.json`

## Calibração de atuadores

Use `neuromesh/config/actuators.example.json` como base para `actuators.json`.

Campos por servo:
- `channel`
- `min_angle`
- `max_angle`
- `home_angle`
- `offset_deg`
- `invert`

Se `NEUROMESH_SERVO_ENABLED=true`, config inválida/faltante falha no startup (fail-fast).
No modo stub, defaults seguros são usados.

## Run (simulado)

```bash
cd neuromesh/apps/neuromesh-edge
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export NEUROMESH_SERVO_ENABLED=false
export NEUROMESH_CAMERA_ENABLED=false
PYTHONPATH=../.. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Run com câmera real

```bash
export NEUROMESH_CAMERA_ENABLED=true
export NEUROMESH_CAMERA_DEVICE=/dev/video0
export NEUROMESH_CAMERA_SIMULATION_FALLBACK=true
PYTHONPATH=../.. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Modo servo real (PCA9685)

```bash
cp ../../config/actuators.example.json ../../config/actuators.json
export NEUROMESH_SERVO_ENABLED=true
export NEUROMESH_SERVO_PROVIDER=pca9685
export NEUROMESH_ACTUATORS_CONFIG=../../config/actuators.json
PYTHONPATH=../.. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Validar via snapshot

```bash
curl http://127.0.0.1:8000/snapshot
```

Verifique:
- `perception.provider`, `perception.device`, `perception.frames_processed`
- `motion.provider`, `motion.servo_enabled`, `motion.calibration_loaded`

## Primeiro bring-up no Orange Pi

1. `ls /dev/video*`
2. teste básico OpenCV com `python -c "import cv2; cap=cv2.VideoCapture('/dev/video0'); print(cap.isOpened())"`
3. valide `actuators.json`
4. suba o edge
5. chame `/snapshot`
6. envie comando manual para `/commands`
7. observe logs JSON (`camera_opened`, `perception_provider_selected`, `command_executed`)
