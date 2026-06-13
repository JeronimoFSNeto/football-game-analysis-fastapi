"""Prompt templates for Sonar AI narrative generation."""

from .schemas import SonarNarrativeRequest


SPORT_KEYWORDS = {
    "basquete": ["nba", "basquete", "basketball", "nbb", "euroleague"],
    "tenis": ["tênis", "tenis", "atp", "wta", "grand slam"],
    "futebol_americano": ["nfl", "super bowl", "futebol americano"],
}


def _detect_sport(competition: str) -> str | None:
    comp_lower = competition.lower()
    for sport, keywords in SPORT_KEYWORDS.items():
        if any(kw in comp_lower for kw in keywords):
            return sport
    return "futebol"


SPORT_CONTEXT = {
    "futebol": "Foco em gols, posse de bola, finalizações, escanteios, cartões.",
    "basquete": "Foco em pontos, rebotes, assistências, aproveitamento de arremessos, turnovers.",
    "tenis": "Foco em games, sets, pontos de quebra, aproveitamento no primeiro serviço, erros não-forçados.",
    "futebol_americano": "Foco em touchdowns, jardas, turnovers, terceiras descidas, field goals.",
}


def build_analysis_prompt(req: SonarNarrativeRequest) -> str:
    sport = _detect_sport(req.game.competition)
    sport_context = SPORT_CONTEXT.get(sport, "")

    signal_lines = []
    for s in req.signals:
        prob_pct = round(s.probability * 100, 1)
        ev = f", EV={s.expectedValue:.4f}" if s.expectedValue is not None else ""
        top_factor = max(s.breakdown, key=s.breakdown.get) if s.breakdown else "—"
        signal_lines.append(
            f"- {s.market} [{s.tier.value.upper()}] "
            f"score={s.score}, prob={prob_pct}%{ev}, "
            f"confidence={s.confidence}, top_factor={top_factor}"
        )

    style_guide = {
        "analytical": "Tom técnico e objetivo, citando números e probabilidades. Justifique cada sinal com dados concretos.",
        "concise": "Extremamente conciso — máximo 2 frases por sinal. Ideal para feed rápido.",
        "coaching": "Tom de recomendação acionável. Explique o que o analista deve observar e quais padrões acompanhar.",
    }.get(req.style, "")

    is_english = req.language == "en-US"
    lang = "en" if is_english else "pt-BR"

    few_shot = """Exemplo de saída esperada:

Input: Jogo: Flamengo vs Palmeiras, Over 1.5 Gols [ELITE] score=82, prob=78%, confiança=Muito Alta
Output:
{
  "overall": "Jogo com forte expectativa de gols. Flamengo ataca bem, mas Palmeiras defende sólido.",
  "signals": [
    {
      "market": "Over 1.5 Gols",
      "headline": "Alta probabilidade de gols",
      "rationale": "Flamengo marca em 90% dos jogos em casa. Over 1.5 ocorreu em 7 dos últimos 10 confrontos diretos.",
      "keyFactor": "Ofensividade do Flamengo",
      "confidencePhrase": "Confiança muito alta baseada em 8 de 10 jogos recentes com mais de 1.5 gols."
    }
  ]
}
"""

    return f"""You are Sonar AI, a sports analysis specialist. Language: {lang}.

Game: {req.game.name}
Competition: {req.game.competition}
{req.game.homeTeam} vs {req.game.awayTeam}
Status: {req.game.status}
Score: {req.game.homeScore or '—'} x {req.game.awayScore or '—'}
Sport context: {sport_context}

Available signals:
{chr(10).join(signal_lines)}

Style: {style_guide}

{few_shot}
Respond EXACTLY in JSON format (no markdown, no code fences):

{{
  "overall": "<single paragraph with holistic match reading>",
  "signals": [
    {{
      "market": "<market name>",
      "headline": "<1-line title>",
      "rationale": "<2-3 sentences explaining why>",
      "keyFactor": "<single most relevant factor>",
      "confidencePhrase": "<confidence statement>"
    }}
  ]
}}
"""
