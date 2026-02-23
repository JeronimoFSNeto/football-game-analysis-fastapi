from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from httpx import ASGITransport, AsyncClient
import main


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"]
    assert "models" in data


@pytest.mark.anyio
async def test_analyze_happy_path(monkeypatch):
    async def fake_run_llm(prompt: str, model: str) -> str:
        return "ok"

    monkeypatch.setattr(main, "run_llm", fake_run_llm)

    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        resp = await client.post("/analyze", json={"match": "Team A vs Team B", "context": "derby"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["analysis"] == "ok"
    assert data["match"] == "Team A vs Team B"


@pytest.mark.anyio
async def test_analyze_validation_error():
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        resp = await client.post("/analyze", json={"match": "x", "context": ""})
    assert resp.status_code == 422
