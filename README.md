# NeuroMesh

Fundação experimental de runtime **core/edge** para robótica de baixo custo. O edge mantém percepção, estado e execução de comandos; um core no desktop acompanha eventos e decide por regras simples.

## O que está implementado

- Dois serviços FastAPI com contratos Pydantic compartilhados.
- Percepção simulada ou detecção de movimento por câmera USB/OpenCV.
- Providers de motion `stub` e PCA9685, com adaptação de hardware isolada.
- Validação de comandos e calibração por JSON: limites de ângulo, offset e inversão.
- Fila limitada de comandos, acknowledgements explícitos e eventos por WebSocket.
- Snapshot operacional, logs JSON e persistência de eventos/snapshot no edge.
- Testes de contratos, persistência, planner, normalização e fluxo core/edge.

| Módulo | Responsabilidade | Código |
| :--- | :--- | :--- |
| Edge | Percepção, estado, comandos e atuadores | [neuromesh-edge](neuromesh/apps/neuromesh-edge) |
| Core | Cliente do edge e planner por regras | [neuromesh-core](neuromesh/apps/neuromesh-core) |
| Contratos | Comandos, eventos e snapshots compartilhados | [packages](neuromesh/packages) |

## Demo local sem hardware

A sequência abaixo mantém câmera e servo físico desabilitados. Use Python 3.11+ e execute os primeiros comandos na raiz deste repositório.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r neuromesh/apps/neuromesh-edge/requirements.txt -r neuromesh/apps/neuromesh-core/requirements.txt -r neuromesh/requirements-dev.txt

cd neuromesh/apps/neuromesh-edge
NEUROMESH_CAMERA_ENABLED=false NEUROMESH_SERVO_ENABLED=false PYTHONPATH=../.. python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Em outro terminal:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/snapshot
```

O serviço core é opcional para inspecionar o edge. Seu setup e configuração estão em [neuromesh-core/README.md](neuromesh/apps/neuromesh-core/README.md).

## Testes

Com o mesmo ambiente virtual ativo, a partir da raiz do repositório:

```bash
cd neuromesh
python -m pytest -q
```

Na revisão de 6 de outubro de 2026, **12 testes passaram** em ambiente Linux/Python 3.12, incluindo o fluxo de cliente core com um processo HTTP edge local. Isso não valida eletrônica ou movimentos físicos.

## Decisões que vale inspecionar

- [Validação e normalização de atuadores](neuromesh/apps/neuromesh-edge/app/modules/motion/actuator_service.py).
- [Entrada de comandos e rejeição de fila cheia](neuromesh/apps/neuromesh-edge/app/api/routes.py).
- [Fluxo core/edge testado](neuromesh/tests/test_edge_core_integration.py).
- [Arquitetura e limitações](neuromesh/docs/architecture.md).
- [ADRs](neuromesh/docs/adr).

## Limites atuais

A percepção atual detecta movimento; o planner usa regras simples. O projeto ainda não implementa uma mesh multi-node completa, navegação autônoma geral ou LLM no loop. A integração física depende da calibração e do ambiente de hardware descritos na documentação.

Este repositório registra uma fundação experimental de arquitetura distribuída; não deve ser interpretado como uma plataforma robótica pronta para produção.
