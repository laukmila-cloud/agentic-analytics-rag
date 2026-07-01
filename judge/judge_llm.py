import json
import re

from app.schemas import JudgeResult
from llm.bedrock_client import BedrockLLM


class JudgeLLM:
    def __init__(self):
        self.llm = BedrockLLM()

    def evaluate(
        self,
        question: str,
        answer: str,
        rag_context: dict,
        analytics_result: dict | None,
    ) -> JudgeResult:
        fallback_result = self._heuristic_evaluation(
            question=question,
            answer=answer,
            rag_context=rag_context,
            analytics_result=analytics_result,
        )

        system_prompt = """
Eres un agente juez especializado en evaluar respuestas de sistemas RAG analíticos.
Debes evaluar la respuesta antes de entregarla al usuario final.
No inventes información. Evalúa únicamente con base en la pregunta, la respuesta,
el contexto RAG y los resultados analíticos entregados.
Devuelve únicamente un JSON válido.
"""

        user_prompt = f"""
Evalúa la siguiente respuesta del sistema agéntico.

Pregunta del usuario:
{question}

Respuesta generada:
{answer}

Contexto RAG:
{rag_context}

Resultado analítico:
{analytics_result}

Criterios de evaluación:
1. Relevancia frente a la pregunta.
2. Uso correcto del contexto RAG.
3. Precisión numérica.
4. Ausencia de alucinaciones.
5. Claridad para usuario de negocio.

Devuelve únicamente este JSON:

{{
  "score": número entre 0 y 10,
  "verdict": "aprobada, aprobada con observaciones o rechazada",
  "numeric_precision": "evaluación breve de precisión numérica",
  "hallucination_risk": "bajo, medio o alto",
  "improvement_suggestion": "mejora concreta si aplica"
}}
"""

        llm_text = self.llm.generate_or_fallback(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback_text="",
            temperature=0.0,
            max_tokens=500,
        )

        if not llm_text:
            return fallback_result

        parsed = self._safe_parse_json(llm_text)

        if not parsed:
            return fallback_result

        return JudgeResult(
            score=float(parsed.get("score", fallback_result.score)),
            verdict=str(parsed.get("verdict", fallback_result.verdict)),
            numeric_precision=str(
                parsed.get("numeric_precision", fallback_result.numeric_precision)
            ),
            hallucination_risk=str(
                parsed.get("hallucination_risk", fallback_result.hallucination_risk)
            ),
            improvement_suggestion=parsed.get(
                "improvement_suggestion",
                fallback_result.improvement_suggestion,
            ),
        )

    def _heuristic_evaluation(
        self,
        question: str,
        answer: str,
        rag_context: dict,
        analytics_result: dict | None,
    ) -> JudgeResult:
        chunks = rag_context.get("chunks", [])

        has_context = len(chunks) > 0
        has_analytics_error = (
            analytics_result is not None
            and analytics_result.get("success") is False
        )

        score = 8.0

        if not has_context:
            score -= 1.0

        if has_analytics_error:
            score -= 1.5

        if len(answer.strip()) < 100:
            score -= 1.0

        if "promedio_indicador" in answer and analytics_result is None:
            score -= 1.0

        score = max(0.0, min(10.0, score))

        hallucination_risk = "Bajo" if has_context else "Medio"

        return JudgeResult(
            score=round(score, 2),
            verdict="Respuesta aprobada por juez heurístico local.",
            numeric_precision=(
                "Sin errores numéricos detectados automáticamente."
                if not has_analytics_error
                else "Existe un error en la consulta o cálculo analítico."
            ),
            hallucination_risk=hallucination_risk,
            improvement_suggestion=(
                "Activar USE_BEDROCK=true para evaluación con Judge LLM en Amazon Bedrock."
            ),
        )

    def _safe_parse_json(self, text: str) -> dict | None:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            return None

        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None