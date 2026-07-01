from fastapi import FastAPI

from app.schemas import ChatRequest, ChatResponse
from orchestrator.agent_orchestrator import AgentOrchestrator

app = FastAPI(
    title="Sistema Agéntico Analítico con LLM + RAG + Tools",
    version="0.1.0",
)

orchestrator = AgentOrchestrator()


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Sistema agéntico activo",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return orchestrator.run(request.question)