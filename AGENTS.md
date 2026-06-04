# Repository Guidelines

## Project Structure
- `main.py` - FastAPI app, request models, routes. Entry point: `analyze_match`.
- `tests/test_api.py` - pytest tests using `pytest-anyio` (`@pytest.mark.anyio`).
- `requirements.txt` / `requirements.lock` - pinned deps; use lockfile for reproducible installs.

## Commands
```bash
# Ambiente já existe em .venv (não recriar)
source .venv/bin/activate         # optional: ativa venv

pip install -r requirements.lock  # reproducible install (se precisar reinstall)
uvicorn main:app --reload         # dev server
pytest -q                         # run tests
```

**Dica:** Use `.venv/bin/python` ou `.venv/bin/pytest` sem ativar o venv.

## Key Dependencies
- `llm-orchestrator` - private git package (git+https...). Required for `/analyze` endpoint.
- Requires `OPENAI_API_KEY` in `.env`.

## Configuration (`.env`)
```env
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT_SECONDS=20
PORT=8000
```

## Gotchas
- LLM calls have a timeout (`anyio.fail_after`). Returns 504 on timeout, 502 on LLM error.
- Tests mock `main.run_llm` with monkeypatch - not using httpx mock.
- No linter/formatter configured.
