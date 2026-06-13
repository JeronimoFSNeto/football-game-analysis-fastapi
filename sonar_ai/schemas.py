"""Pydantic models for Sonar AI — LLM narrative layer."""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class SonarTier(str, Enum):
    ELITE = "elite"
    FORTE = "forte"
    MODERADO = "moderado"
    ESPECULATIVO = "especulativo"


class SignalInput(BaseModel):
    """A single Sonar market signal for a game."""
    market: str = Field(..., description="Market name, e.g. 'Over 1.5 Gols'")
    category: str = Field(..., description="Market category: goals|corners|cards|result|value")
    score: int = Field(..., ge=0, le=100, description="Sonar Score (0-100)")
    tier: SonarTier
    confidence: str = Field(..., description="Muito Alta|Alta|Média|Baixa")
    probability: float = Field(..., ge=0, le=1)
    expectedValue: Optional[float] = None
    breakdown: dict = Field(default_factory=dict, description="Factor breakdown: form, h2h, offense, etc.")


class GameContextInput(BaseModel):
    """Game metadata for narrative context."""
    id: int
    name: str = Field(..., description="e.g. 'Flamengo vs Palmeiras'")
    competition: str = Field(..., description="e.g. 'Brasileirão Série A'")
    homeTeam: str
    awayTeam: str
    status: str = Field(..., description="scheduled|in_progress|completed")
    homeScore: Optional[int] = None
    awayScore: Optional[int] = None


class SonarNarrativeRequest(BaseModel):
    """Request: game context + array of Sonar signals to narrate."""
    game: GameContextInput
    signals: list[SignalInput] = Field(..., min_length=1, max_length=30)
    language: str = Field(default="pt-BR", pattern="^(pt-BR|en-US)$")
    style: str = Field(default="analytical", pattern="^(analytical|concise|coaching)$")


class SignalNarrative(BaseModel):
    """Narrative output for a single signal."""
    market: str
    headline: str = Field(..., description="Short 1-line summary")
    rationale: str = Field(..., description="2-3 sentence explanation of why")
    keyFactor: str = Field(..., description="The single most relevant factor")
    confidencePhrase: str = Field(..., description="e.g. 'Confiança muito alta baseada em 8 de 10 jogos recentes'")


class SonarNarrativeResponse(BaseModel):
    """Response: overall assessment + per-signal narratives."""
    gameId: int
    overall: str = Field(..., description="1-paragraph holistic match reading")
    signals: list[SignalNarrative]
    model: str = Field(default="", description="LLM model used")
