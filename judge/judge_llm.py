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
6. Suficiencia del corpus para responder la pregunta.

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

        best_raw_score = max(
            [
                chunk.get("raw_score", chunk.get("rerank_score", 0))
                for chunk in chunks
            ],
            default=0,
        )

        relevance_threshold = 0.15
        has_relevant_context = (
            len(chunks) > 0
            and best_raw_score >= relevance_threshold
        )

        has_analytics_error = (
            analytics_result is not None
            and analytics_result.get("success") is False
        )

        question_lower = question.lower()

        out_of_domain_keywords = [
            "receta",
            "pasta",
            "cocina",
            "ingredientes",
            "astronomía",
            "planeta",
            "galaxia",
            "fútbol",
            "película",
            "canción",
            "viaje",
            "hotel",
            "turismo",
            "moda",
            "maquillaje",
        ]

        domain_keywords = [
            "indicador",
            "kpi",
            "siniestralidad",
            "regional",
            "promedio",
            "desempeño",
            "costo",
            "ingreso",
            "tasa",
            "porcentaje",
            "brecha",
            "variación",
            "reporte",
            "observabilidad",
            "métrica",
        ]

        appears_out_of_domain = any(
            keyword in question_lower
            for keyword in out_of_domain_keywords
        )

        appears_in_domain = any(
            keyword in question_lower
            for keyword in domain_keywords
        )

        score = 8.0

        if not has_relevant_context:
            score -= 2.0

        if appears_out_of_domain and not appears_in_domain:
            score -= 2.0

        if appears_out_of_domain and not has_relevant_context:
            score -= 1.0

        if has_analytics_error:
            score -= 1.5

        if len(answer.strip()) < 100:
            score -= 1.0

        if "promedio_indicador" in answer and analytics_result is None:
            score -= 1.0

        score = max(0.0, min(10.0, score))

        if appears_out_of_domain and not appears_in_domain:
            hallucination_risk = "Alto"
            verdict = "Respuesta aprobada con observaciones por juez heurístico local."
            improvement = (
                "La consulta parece estar fuera del dominio del corpus. "
                "Se recomienda responder indicando que la información disponible no es suficiente "
                "o ampliar el corpus documental para cubrir ese tema."
            )
        elif not has_relevant_context:
            hallucination_risk = "Alto"
            verdict = "Respuesta aprobada con observaciones por juez heurístico local."
            improvement = (
                "La consulta no está suficientemente soportada por el corpus documental recuperado. "
                "Se recomienda validar las fuentes, ampliar el corpus o advertir la falta de evidencia."
            )
        elif has_analytics_error:
            hallucination_risk = "Medio"
            verdict = "Respuesta aprobada con observaciones por juez heurístico local."
            improvement = (
                "Revisar la consulta analítica, la disponibilidad del archivo Parquet "
                "o la estructura de columnas usada por la herramienta."
            )
        else:
            hallucination_risk = "Bajo"
            verdict = "Respuesta aprobada por juez heurístico local."
            improvement = (
                "Activar USE_BEDROCK=true para evaluación con Judge LLM en Amazon Bedrock."
            )

        return JudgeResult(
            score=round(score, 2),
            verdict=verdict,
            numeric_precision=(
                "Sin errores numéricos detectados automáticamente."
                if not has_analytics_error
                else "Existe un error en la consulta o cálculo analítico."
            ),
            hallucination_risk=hallucination_risk,
            improvement_suggestion=improvement,
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