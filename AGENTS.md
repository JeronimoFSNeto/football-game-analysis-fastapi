# Repository Guidelines

## Project Structure & Module Organization
- `main.py` defines the FastAPI app, request models, and routes.
- `requirements.txt` pins Python dependencies (including LLM SDKs and pytest).
- `tests/` contains pytest-based API tests (e.g., `tests/test_api.py`).
- `.env.example` documents required environment variables; copy to `.env` for local runs.
- `docs/` exists for documentation but is currently empty.

## Build, Test, and Development Commands
- `python -m venv .venv` then `source .venv/bin/activate`: create/activate a local virtualenv.
- `pip install -r requirements.txt`: install dependencies.
- `uvicorn main:app --reload`: run the API locally with auto-reload.
- `pytest`: run the test suite.

## Coding Style & Naming Conventions
- Language: Python 3. Use 4-space indentation.
- Keep route handlers small and explicit; prefer clear names like `analyze_match`.
- Pydantic models should use `CamelCase` class names (e.g., `AnalysisRequest`).
- No formatter or linter is configured yet; keep imports ordered and avoid unused imports.

## Testing Guidelines
- Frameworks listed: `pytest`, `pytest-asyncio` in `requirements.txt`.
- Place tests under `tests/` and name files `test_*.py`.
- Use `pytest` for all runs; add async tests with `pytest.mark.asyncio` when needed.

## Commit & Pull Request Guidelines
- Git history contains a single commit (“FastAPI football analysis init”), so no convention is established.
- Suggested PR contents: short summary, how to run locally, and any config/env changes.
- If changes affect API responses, include example request/response snippets.

## Security & Configuration Tips
- Store secrets in `.env` (not committed). Keep `.env.example` updated with required keys.
- The API exposes `/` and `/analyze`; avoid logging sensitive prompt data.
