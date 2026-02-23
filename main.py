from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
import anyio
import inspect
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Football Game Analysis API")

DEFAULT_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT_SECONDS = float(os.environ.get("LLM_TIMEOUT_SECONDS", "20"))


class AnalysisRequest(BaseModel):
    match: str = Field(..., min_length=3, max_length=500)
    context: str = Field(default="", max_length=2000)


class AnalysisResponse(BaseModel):
    match: str
    analysis: str
    model: str = DEFAULT_MODEL

@app.get("/")
async def root():
    return {"status": "Football LLM API running!", "models": [DEFAULT_MODEL]}


def _get_llm_runner():
    try:
        import llm_orchestrator as llo
    except Exception as exc:
        raise RuntimeError("llm-orchestrator not available") from exc

    if hasattr(llo, "run"):
        return llo.run
    if hasattr(llo, "LLMOrchestrator"):
        return llo.LLMOrchestrator().run

    raise RuntimeError("llm-orchestrator has no supported entrypoint")


async def run_llm(prompt: str, model: str) -> str:
    runner = _get_llm_runner()

    def _call_sync():
        try:
            return runner(prompt=prompt, model=model)
        except TypeError:
            return runner(prompt)

    if inspect.iscoroutinefunction(runner):
        try:
            return await runner(prompt=prompt, model=model)
        except TypeError:
            return await runner(prompt)

    return await anyio.to_thread.run_sync(_call_sync)

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_match(request: AnalysisRequest):
    prompt = f"Analise: {request.match}. Contexto: {request.context}"
    try:
        with anyio.fail_after(LLM_TIMEOUT_SECONDS):
            result = await run_llm(prompt, DEFAULT_MODEL)
    except TimeoutError:
        raise HTTPException(status_code=504, detail="LLM timeout")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")

    return {"match": request.match, "analysis": result, "model": DEFAULT_MODEL}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
