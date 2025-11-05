# Codex Aeturnum v106 - Usage Examples

## Quick Start

### 1. Install Dependencies

```bash
cd builds/codex-v106

# Install orchestrator dependencies
cd services/orchestrator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate

# Install API gateway dependencies
cd ../api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate

cd ../..
```

### 2. Start Services

Open two terminal windows:

**Terminal 1 - Start Orchestrator:**
```bash
cd builds/codex-v106
make orch
```

**Terminal 2 - Start API Gateway:**
```bash
cd builds/codex-v106
make api
```

## API Examples

### Example 1: Compile a Workflow

Compile glyphs into a DAG without executing:

```bash
curl -X POST http://localhost:8010/workflows/compile \
  -H "Content-Type: application/json" \
  -d '{"glyph":"🌀;🌞;🧾"}'
```

Response:
```json
{
  "ok": true,
  "dag_digest": "e2d6860e932818896bb0a2b7bb1a95f5154e2311c65886e06a274454d149279b",
  "tasks": ["00_verify", "01_invoke", "02_audit"]
}
```

### Example 2: Execute a Workflow

Submit a workflow for execution:

```bash
curl -X POST http://localhost:8010/runs \
  -H "Content-Type: application/json" \
  -d '{"glyph":"🌀;🌞;🧾;🛡","tenant":"production"}'
```

Response:
```json
{
  "run_id": "ea994482-0f43-4054-8976-4dc4a4665f05",
  "dag_digest": "e2d6860e932818896bb0a2b7bb1a95f5154e2311c65886e06a274454d149279b",
  "state": "queued"
}
```

### Example 3: Full Workflow Sequence

Execute the complete 10-step workflow:

```bash
curl -X POST http://localhost:8010/runs \
  -H "Content-Type: application/json" \
  -d '{"glyph":"🌀;🌞;🧾;🛡;🔮;🛡‍🔥;🚦;⚖️;🌈;♾","tenant":"demo"}'
```

### Example 4: Stream Execution Events

Watch workflow execution in real-time via Server-Sent Events:

```bash
curl -N http://localhost:8010/events/stream
```

Sample output:
```
data: {"type":"step","task":"00_verify","digest":"abc123...","run":"ea994482..."}
data: {"type":"step","task":"01_invoke","digest":"def456...","run":"ea994482..."}
data: {"type":"run_done","head":"789xyz...","run":"ea994482..."}
```

### Example 5: Via API Gateway

Submit workflow through the API gateway:

```bash
curl -X POST http://localhost:8000/submit \
  -H "Content-Type: application/json" \
  -d '{"glyph":"🌀;🌞;🧾","tenant":"api-test"}'
```

## Glyph Reference

### Available Glyphs

| Glyph | Step Name | Purpose | Example Use |
|-------|-----------|---------|-------------|
| 🌀 | verify | Verify inputs and prerequisites | Security checks, validation |
| 🌞 | invoke | Invoke the primary operation | Main business logic |
| 🧾 | audit | Generate audit trail | Compliance logging |
| 🛡 | scan | Security scan | Vulnerability scanning |
| 🔮 | attest | Create attestation | Cryptographic signing |
| 🛡‍🔥 | sanctify | Policy compliance check | Policy enforcement |
| 🚦 | rollout | Progressive rollout | Canary deployment |
| ⚖️ | judge | Decision gate | Quality gate |
| 🌈 | deploy | Deploy to target | Production deployment |
| ♾ | continuum | Close and finalize | Cleanup and completion |

### Glyph Syntax

Glyphs can be separated by:
- Semicolons: `🌀;🌞;🧾`
- Newlines:
  ```
  🌀
  🌞
  🧾
  ```

Text step names are also supported:
```
verify;invoke;audit
```

Mixed format:
```
🌀;invoke;🧾
```

## Python API

### Direct Use of Core Libraries

```python
import sys
sys.path.insert(0, 'packages/core/src')

from codex_core.holonous import compile_glyphs
from codex_core.compile_dag import glyphs_to_dag
from codex_core.orch import Run

# Compile glyphs
result = compile_glyphs('🌀;🌞;🧾')
print(result)
# {'ok': True, 'steps': ['verify', 'invoke', 'audit'], 'explain': '...'}

# Create DAG
dag = glyphs_to_dag('🌀;🌞;🧾')
print(f"DAG digest: {dag.digest()}")
print(f"Tasks: {list(dag.tasks.keys())}")
print(f"Execution order: {dag.topo()}")
```

## Integration Examples

### CI/CD Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy with Codex
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Execute deployment workflow
        run: |
          curl -X POST http://orchestrator:8010/runs \
            -H "Content-Type: application/json" \
            -d '{"glyph":"🌀;🌞;🧾;🛡;🔮;🛡‍🔥;🚦;⚖️;🌈;♾","tenant":"ci"}'
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  orchestrator:
    build: ./services/orchestrator
    ports:
      - "8010:8010"
    environment:
      - PYTHONPATH=/app/packages/core/src
  
  api:
    build: ./services/api
    ports:
      - "8000:8000"
    environment:
      - ORCHESTRATOR_URL=http://orchestrator:8010
    depends_on:
      - orchestrator
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8010

# Kill the process
kill -9 <PID>
```

### Import Errors

Ensure PYTHONPATH is set correctly:

```bash
export PYTHONPATH="$(pwd)/packages/core/src"
```

### Virtual Environment Issues

If the virtual environment is corrupted, recreate it:

```bash
rm -rf services/orchestrator/.venv
cd services/orchestrator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Development

### Adding Custom Plugins

Edit `services/orchestrator/plugins.py`:

```python
@task("custom.my_task")
def my_custom_task(param1: str = "default", **kw):
    # Your custom logic here
    return {"result": "success", "processed": param1}
```

Update `holonous.py` to map a glyph:

```python
GLYPH_MAP = {
    # ... existing glyphs ...
    '🎯': 'my_task',
}
```

### Testing

Run the test suite:

```bash
cd builds/codex-v106
export PYTHONPATH="$(pwd)/packages/core/src"

# Test glyph compilation
python3 -c "
from codex_core.holonous import compile_glyphs
assert compile_glyphs('🌀;🌞;🧾')['ok'] == True
print('✓ Glyph compilation works')
"

# Test DAG creation
python3 -c "
from codex_core.compile_dag import glyphs_to_dag
dag = glyphs_to_dag('🌀;🌞;🧾')
assert len(dag.tasks) == 3
print('✓ DAG creation works')
"
```

## License

ECCL-1.0 — Eternal Cryptographic Commons License

See LICENSE file for full details.
