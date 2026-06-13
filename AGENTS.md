# Repository Guidelines

## Project Structure
- `main.py` - FastAPI app, request models, routes. Entry point: `analyze_match`.
- `sonar_ai/` - Sonar AI module (LLM narrative layer).
  - `schemas.py` - Pydantic request/response models (already defined).
  - `prompts.py` - Prompt templates. **TODO**: implement `build_analysis_prompt`.
  - `router.py` - FastAPI router with `/api/v1/sonar/ai/narrate` and `/radar`.
    **TODO**: fix imports and register in `main.py`.
- `tests/test_sonar_ai.py` - Tests using monkeypatch mock.
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
- `router.py` uses `from main import run_llm` (late import to avoid circular dep).

## Sonar AI — Next Steps for the Agent

The `sonar_ai/` module is scaffolded but needs implementation. The agent must:

### 1. Register router in `main.py`
Add `app.include_router(sonar_ai_router)` at the end of `main.py`:
```python
from sonar_ai.router import router as sonar_ai_router
app.include_router(sonar_ai_router)
```
Update the `app.title` to `"Sonar AI — Inteligência Esportiva"`.

### 2. Fix `router.py` late import
`router.py` does `from main import run_llm` inside the endpoint function.
This works because the router is registered after `main` is loaded, but the agent
should verify. Alternative: move `run_llm` to a shared module or pass as dependency.

### 3. Implement `prompts.py` `build_analysis_prompt`
The stub builds a basic prompt. The agent can improve it by:
- Adding few-shot examples for better JSON output
- Tuning style instructions per `req.style` (analytical / concise / coaching)
- Adding sport-specific context if `req.game.competition` hints at basketball/tennis

### 4. Fix tests
`test_sonar_ai.py` has known issues:
- Line `monkeypatch.setattr("sonar_ai.router.run_llm", _mock_llm)` — `run_llm` is
  imported locally in `narrate()`, so `sonar_ai.router.run_llm` does not exist
  as a module attribute. Fix: either:
  - Mock `main.run_llm` instead
  - Or refactor `run_llm` into a shared module and mock that
- The timeout test's `base_path="http://test"` should be `base_url="http://test"`

### 5. Verify with pytest
```bash
.venv/bin/pytest tests/test_sonar_ai.py -v
```
Expected: 1 pass (narrate endpoint), 1 pass (timeout) after mocking fix.

### 6. Integration test (manual)
```bash
curl -X POST http://localhost:8000/api/v1/sonar/ai/narrate \
  -H "Content-Type: application/json" \
  -d '{
    "game": {"id": 1, "name": "Flamengo vs Palmeiras", "competition": "Brasileirão", "homeTeam": "Flamengo", "awayTeam": "Palmeiras", "status": "scheduled"},
    "signals": [{"market": "Over 1.5 Gols", "category": "goals", "score": 82, "tier": "elite", "confidence": "Muito Alta", "probability": 0.78, "expectedValue": 0.12, "breakdown": {"form": 80, "h2h": 75, "offense": 85, "defense": 40}}]
  }'
```

## Branding
- Platform: **Sonar**
- This module: **Sonar AI** — LLM narrative layer
- Calling the agent: `opencode "implemente Sonar AI"`
