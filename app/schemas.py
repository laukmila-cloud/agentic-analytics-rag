from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3)


class ToolCall(BaseModel):
    tool_name: str
    input: dict
    output: dict | str | None = None
    success: bool = True


class JudgeResult(BaseModel):
    score: float
    verdict: str
    numeric_precision: str
    hallucination_risk: str
    improvement_suggestion: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
    tool_calls: list[ToolCall] = []
    judge: JudgeResult | None = None
    metrics: dict = {}