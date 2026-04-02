# neuromesh-core

Runtime core para Desktop (Linux/Windows) com planner por regras e cliente Edge.

## Configuração

Copie `.env.example` e ajuste para o IP do edge:

```bash
cp .env.example .env
```

Exemplo para Desktop Windows apontando para Orange Pi em `192.168.1.100`:

```env
NEUROMESH_EDGE_HTTP_BASE=http://192.168.1.100:8000
NEUROMESH_EDGE_WS_URL=ws://192.168.1.100:8000/events
```

## Run (Desktop)

### Linux/macOS
```bash
cd neuromesh/apps/neuromesh-core
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export $(cat .env | xargs)  # opcional
PYTHONPATH=../.. uvicorn app.main:app --host ${NEUROMESH_HOST:-0.0.0.0} --port ${NEUROMESH_PORT:-8010}
```

### Windows PowerShell
```powershell
cd neuromesh/apps/neuromesh-core
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Get-Content .env | ForEach-Object {
  if ($_ -match '^(.*?)=(.*)$') { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2]) }
}
$env:PYTHONPATH="../.."
uvicorn app.main:app --host ${env:NEUROMESH_HOST} --port ${env:NEUROMESH_PORT}
```
