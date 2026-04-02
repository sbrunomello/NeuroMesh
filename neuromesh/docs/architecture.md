# NeuroMesh Architecture (Hardened Foundation)

## Visão

NeuroMesh mantém arquitetura **edge-first + distribuída + event-driven**:
- **Edge:** percepção, estado, execução de comandos e persistência mínima.
- **Core:** consumo de eventos e decisão por regras simples.
- **Comunicação:** HTTP (`/commands`, `/snapshot`) + WebSocket (`/events`).

## PR2: integração de hardware real sem quebrar foundation

### Percepção
- `PerceptionService` seleciona provider por configuração.
- Providers atuais:
  - `simulated`
  - `opencv_motion` (USB camera + background subtraction)
- Falhas de câmera não matam runtime: com `NEUROMESH_CAMERA_SIMULATION_FALLBACK=true`, edge cai para simulação.

### Motion/atuação
- `ActuatorService` centraliza validação/normalização:
  - valida contrato (`position` int)
  - aplica `offset_deg`
  - aplica `invert`
  - aplica `clamp` em `[min_angle, max_angle]`
- Provider motion configurável:
  - `stub`
  - `pca9685` (via adapter dedicado)
- Hardware isolado por `ServoHardwareAdapter` (NoOp + PCA9685).

### Calibração
- Calibração externa via `NEUROMESH_ACTUATORS_CONFIG`.
- Se servo real habilitado e arquivo inválido/faltante: fail-fast no startup.
- Em stub: defaults seguros são carregados.

### Observabilidade
- Snapshot inclui seção `perception` e `motion` com provider ativo, status de câmera/hardware, frames processados e calibração carregada.
- Logs JSON explícitos para seleção de provider, erro de captura e execução de comando.

## Limitações atuais
- Detecção de visão é motion-only (sem face tracking neste PR).
- Adapter PCA9685 é baseline para Orange Pi; pode exigir ajustes de timing conforme setup elétrico.
- Sem mesh multi-node completa e sem LLM (deliberado no v1).
