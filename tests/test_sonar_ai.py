"""Tests for Sonar AI router.

Mock strategy: monkeypatch main.run_llm to return a canned JSON response.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from httpx import AsyncClient, ASGITransport
from sonar_ai.router import router
from sonar_ai.schemas import (
    SonarNarrativeRequest,
    GameContextInput,
    SignalInput,
)


@pytest.fixture
def sample_request():
    return SonarNarrativeRequest(
        game=GameContextInput(
            id=1,
            name="Flamengo vs Palmeiras",
            competition="Brasileirão Série A",
            homeTeam="Flamengo",
            awayTeam="Palmeiras",
            status="scheduled",
        ),
        signals=[
            SignalInput(
                market="Over 1.5 Gols",
                category="goals",
                score=82,
                tier="elite",
                confidence="Muito Alta",
                probability=0.78,
                expectedValue=0.12,
                breakdown={"form": 80, "h2h": 75, "offense": 85, "defense": 40},
            ),
            SignalInput(
                market="BTTS Sim",
                category="goals",
                score=65,
                tier="forte",
                confidence="Alta",
                probability=0.62,
                breakdown={"form": 70, "h2h": 60, "offense": 75, "defense": 45},
            ),
        ],
    )


async def _mock_llm(prompt: str, model: str) -> str:
    return """{
        "overall": "Jogo com expectativa de gols. Flamengo ataca bem, mas Palmeiras defende sólido.",
        "signals": [
            {
                "market": "Over 1.5 Gols",
                "headline": "Alta probabilidade de gols",
                "rationale": "Flamengo marca em 90% dos jogos em casa.",
                "keyFactor": "Ofensividade do Flamengo",
                "confidencePhrase": "Confiança muito alta baseada em 8 de 10 jogos."
            }
        ]
    }"""


@pytest.mark.anyio
async def test_narrate_endpoint(monkeypatch, sample_request):
    monkeypatch.setattr("main.run_llm", _mock_llm)

    from main import app
    app.include_router(router)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = sample_request.model_dump()
        response = await client.post("/api/v1/sonar/ai/narrate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["gameId"] == 1
    assert "overall" in data
    assert len(data["signals"]) == 1
    assert data["signals"][0]["market"] == "Over 1.5 Gols"


@pytest.mark.anyio
async def test_narrate_timeout(monkeypatch, sample_request):
    async def _slow(*args, **kwargs):
        import anyio
        await anyio.sleep(10)

    monkeypatch.setattr("main.run_llm", _slow)
    monkeypatch.setattr("sonar_ai.router.LLM_TIMEOUT_SECONDS", 0.1)

    from main import app
    app.include_router(router)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = sample_request.model_dump()
        response = await client.post("/api/v1/sonar/ai/narrate", json=payload)

    assert response.status_code == 504
