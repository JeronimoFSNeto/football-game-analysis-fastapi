from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Football Game Analysis API")

class AnalysisRequest(BaseModel):
    match: str
    context: str = ""

@app.get("/")
async def root():
    return {"status": "Football LLM API running!", "models": ["gpt-4o-mini"]}

@app.post("/analyze")
async def analyze_match(request: AnalysisRequest, background_tasks: BackgroundTasks):
    # IMPORT llm-orchestrator no Render
    prompt = f"Analise: {request.match}. Contexto: {request.context}"
    # result = llm_orchestrator.run(prompt)  # Render instala
    return {"match": request.match, "analysis": f"Demo: {prompt}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF
