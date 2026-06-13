"""Sonar AI router — LLM-powered narrative layer for Sonar analysis.

Endpoints:
  POST /api/v1/sonar/ai/narrate  — Full narrative for a game's signals
  POST /api/v1/sonar/ai/radar    — Quick radar feed narrative (concise style)

TODO: Register this router in main.py with app.include_router(sonar_ai_router)
"""

from fastapi import APIRouter, HTTPException
import anyio
import os
import json
import re

from .schemas import SonarNarrativeRequest, SonarNarrativeResponse, SignalNarrative
from .prompts import build_analysis_prompt

router = APIRouter(prefix="/api/v1/sonar/ai", tags=["Sonar AI"])

LLM_TIMEOUT_SECONDS = float(os.environ.get("LLM_TIMEOUT_SECONDS", "20"))
DEFAULT_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


@router.post("/narrate", response_model=SonarNarrativeResponse)
async def narrate(request: SonarNarrativeRequest):
    """Generate full narrative for a game's Sonar signals.

    Calls the LLM with a structured prompt and returns:
      - overall: holistic match reading (1 paragraph)
      - signals: per-market narrative (headline, rationale, keyFactor, confidencePhrase)
    """
    from main import run_llm  # noqa: late import avoids circular dep

    prompt = build_analysis_prompt(request)

    try:
        with anyio.fail_after(LLM_TIMEOUT_SECONDS):
            raw = await run_llm(prompt, DEFAULT_MODEL)
    except TimeoutError:
        raise HTTPException(status_code=504, detail="LLM timeout")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")

    try:
        data = _extract_json(raw)
    except (json.JSONDecodeError, KeyError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to parse LLM output as JSON: {exc}",
        )

    return SonarNarrativeResponse(
        gameId=request.game.id,
        overall=data["overall"],
        signals=[SignalNarrative(**s) for s in data["signals"]],
        model=DEFAULT_MODEL,
    )


@router.post("/radar", response_model=list[SonarNarrativeResponse])
async def narrate_radar(requests: list[SonarNarrativeRequest]):
    """Batch narrative for multiple games (Radar feed).

    Calls narrate for each game sequentially.
    Optimize with concurrent calls if latency is an issue.
    """
    results = []
    for req in requests:
        req.style = "concise"
        result = await narrate(req)
        results.append(result)
    return results
