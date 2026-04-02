# NeuroMesh Architecture (Hardened Foundation)

## Visão

NeuroMesh mantém arquitetura **edge-first + distribuída + event-driven**:
- **Edge:** percepção, estado, execução de comandos e persistência mínima.
- **Core:** consumo de eventos e decisão por regras simples.
- **Comunicação:** HTTP (`/commands`, `/snapshot`) + WebSocket (`/events`).

## Hardening aplicado

1. **Config operacional por env** (sem hardcode para runtime distribuído).
2. **Atuadores generalizados** (sem acoplamento a `servo_1`; usa `command.target`).
3. **Domínio interno explícito** em `modules/*` (edge) e `bridge/*` (core).
4. **Persistência mínima** (`events.jsonl`, `snapshot.json`) com tolerância a falhas.
5. **Contracts endurecidos** (`schema_version`, validações, `CommandAck`).
6. **Métricas runtime úteis** (`events_published`, `events_persisted`, `commands_rejected`, etc.).
7. **Testes de integração essenciais** cobrindo fluxo edge/core.

## Limitações atuais da foundation

- Sem hardware real de atuadores/sensores.
- Sem percepção real de câmera.
- Sem malha multi-node completa.
- Sem LLM (deliberado no v1).
