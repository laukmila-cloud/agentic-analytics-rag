import time

from app.schemas import ChatResponse, ToolCall
from judge.judge_llm import JudgeLLM
from llm.bedrock_client import BedrockLLM
from observability.metrics import MetricsLogger
from tools.kpi_calculator import KPICalculator
from workers.analytics_worker import AnalyticsWorker
from workers.rag_worker import RAGWorker
from workers.report_worker import ReportWorker


class AgentOrchestrator:
    def __init__(self):
        self.rag_worker = RAGWorker()
        self.analytics_worker = AnalyticsWorker()
        self.report_worker = ReportWorker()
        self.judge = JudgeLLM()
        self.metrics_logger = MetricsLogger()
        self.kpi_calculator = KPICalculator()
        self.llm = BedrockLLM()

    def run(self, question: str) -> ChatResponse:
        start_time = time.perf_counter()
        tool_calls: list[ToolCall] = []

        # 1. Recuperación documental
        rag_result = self.rag_worker.search(question)

        tool_calls.append(
            ToolCall(
                tool_name="rag_search",
                input={"question": question},
                output=rag_result,
                success=True,
            )
        )

        analytics_result = None
        kpi_result = None

        # 2. Consulta analítica estructurada
        if self._requires_analytics(question):
            analytics_result = self.analytics_worker.analyze(question)

            tool_calls.append(
                ToolCall(
                    tool_name="duckdb_analytics",
                    input={"question": question},
                    output=analytics_result,
                    success=analytics_result.get("success", False),
                )
            )

        # 3. Cálculo KPI complementario
        if analytics_result and analytics_result.get("success"):
            data = analytics_result.get("data", [])

            if len(data) >= 2 and "promedio_indicador" in data[0]:
                value_a = data[0]["promedio_indicador"]
                value_b = data[1]["promedio_indicador"]

                kpi_result = self.kpi_calculator.calculate_gap(
                    value_a=value_a,
                    value_b=value_b,
                    label_a=data[0].get("regional", "Grupo A"),
                    label_b=data[1].get("regional", "Grupo B"),
                )

                tool_calls.append(
                    ToolCall(
                        tool_name="kpi_calculator",
                        input={
                            "value_a": value_a,
                            "value_b": value_b,
                        },
                        output=kpi_result,
                        success=kpi_result.get("success", False),
                    )
                )

        # 4. Composición de respuesta
        answer = self._compose_answer(
            question=question,
            rag_result=rag_result,
            analytics_result=analytics_result,
        )

        if kpi_result:
            answer += (
                "\n\n### Cálculo complementario\n\n"
                f"- Diferencia absoluta: **{kpi_result.get('absolute_gap')} puntos**.\n"
                f"- Valor más alto: **{kpi_result.get('higher_value')}**.\n"
            )

        # 5. Generación de reporte PDF
        if self._requires_report(question):
            report_result = self.report_worker.generate(
                title="Reporte analítico generado por el sistema",
                content=answer,
            )

            tool_calls.append(
                ToolCall(
                    tool_name="pdf_report_generator",
                    input={
                        "title": "Reporte analítico generado por el sistema",
                    },
                    output=report_result,
                    success=report_result.get("success", False),
                )
            )

            if report_result.get("success"):
                answer += (
                    "\n\n### Reporte generado\n\n"
                    "El reporte PDF fue creado correctamente y está disponible para descarga desde la interfaz."
                )

        # 6. Evaluación con agente juez
        judge_result = self.judge.evaluate(
            question=question,
            answer=answer,
            rag_context=rag_result,
            analytics_result=analytics_result,
        )

        # 7. Métricas de observabilidad
        elapsed = time.perf_counter() - start_time

        total_tools = len(tool_calls)
        successful_tools = sum(1 for call in tool_calls if call.success)

        tool_success_rate = (
            successful_tools / total_tools
            if total_tools > 0
            else 0
        )

        calculation_error_rate = self._calculate_error_rate(
            analytics_result=analytics_result,
            kpi_result=kpi_result,
        )

        rag_chunks = rag_result.get("chunks", [])
        rag_best_score = max(
            [chunk.get("score", 0) for chunk in rag_chunks],
            default=0,
        )

        rag_has_relevant_chunk = rag_best_score >= 0.75

        estimated_tokens = len(question.split()) + len(answer.split())

        # Estimación local simple para demo.
        # En Bedrock real debe calcularse con input_tokens/output_tokens
        # y la tarifa del modelo seleccionado.
        estimated_cost_usd = round((estimated_tokens / 1000) * 0.00025, 6)

        metrics = {
            "tool_success_rate": round(tool_success_rate, 4),
            "tools_total": total_tools,
            "tools_success": successful_tools,
            "judge_score": judge_result.score,
            "ttl_seconds": round(elapsed, 4),
            "estimated_cost_usd": estimated_cost_usd,
            "calculation_error_rate": calculation_error_rate,
            "rag_latency_seconds": rag_result.get("latency_seconds", 0),
            "rag_corpus_coverage": 1.0 if rag_has_relevant_chunk else 0.0,
            "rag_chunks_found": len(rag_chunks),
            "rag_best_score": round(rag_best_score, 4),
            "tokens_estimated": estimated_tokens,
            "avg_tokens_per_session": estimated_tokens,
            "threshold_tool_success_rate": 0.95,
            "threshold_judge_score": 7.5,
            "threshold_ttl_seconds": 10,
            "threshold_cost_usd": 0.05,
            "threshold_calculation_error_rate": 0.03,
            "threshold_rag_latency_seconds": 2,
            "threshold_rag_corpus_coverage": 0.85,
        }

        self.metrics_logger.write(metrics)

        return ChatResponse(
            answer=answer,
            sources=rag_result.get("sources", []),
            tool_calls=tool_calls,
            judge=judge_result,
            metrics=metrics,
        )

    def _calculate_error_rate(
        self,
        analytics_result: dict | None,
        kpi_result: dict | None,
    ) -> float:
        calculation_checks = []

        if analytics_result is not None:
            calculation_checks.append(analytics_result.get("success", False))

        if kpi_result is not None:
            calculation_checks.append(kpi_result.get("success", False))

        if not calculation_checks:
            return 0.0

        failed_checks = sum(1 for check in calculation_checks if not check)

        return round(failed_checks / len(calculation_checks), 4)

    def _requires_analytics(self, question: str) -> bool:
        keywords = [
            "kpi",
            "indicador",
            "promedio",
            "total",
            "tasa",
            "porcentaje",
            "comparar",
            "comparación",
            "variación",
            "mes",
            "regional",
            "costo",
            "ingreso",
            "siniestralidad",
            "desempeño",
        ]

        return any(keyword in question.lower() for keyword in keywords)

    def _requires_report(self, question: str) -> bool:
        keywords = [
            "reporte",
            "pdf",
            "informe",
            "descargar",
            "documento",
        ]

        return any(keyword in question.lower() for keyword in keywords)

    def _compose_answer(
        self,
        question: str,
        rag_result: dict,
        analytics_result: dict | None,
    ) -> str:
        context_text = self._format_rag_context_for_prompt(rag_result)
        analytics_text = self._format_analytics_for_prompt(analytics_result)

        fallback_answer = self._compose_local_executive_answer(
            question=question,
            rag_result=rag_result,
            analytics_result=analytics_result,
        )

        system_prompt = """
Eres un analista senior de datos y desempeño financiero.
Debes responder como un asistente ejecutivo de IA: claro, analítico, concreto y trazable.
No copies el contexto literalmente.
No inventes datos.
Usa el contexto documental solo para interpretar.
Usa los datos estructurados para sustentar cifras.
Si la información es insuficiente, dilo explícitamente.
"""

        user_prompt = f"""
Pregunta del usuario:
{question}

Contexto documental recuperado:
{context_text}

Resultado analítico estructurado:
{analytics_text}

Redacta una respuesta en español con tono profesional y ejecutivo.
La respuesta debe incluir:

1. Respuesta directa.
2. Interpretación de negocio.
3. Evidencia numérica si existe.
4. Relación con el contexto documental.
5. Recomendación o lectura final.
6. Limitaciones, si aplica.

Evita responder como si solo estuvieras mostrando documentos.
Redacta como una IA analítica que sintetiza la información.
"""

        return self.llm.generate_or_fallback(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback_text=fallback_answer,
            temperature=0.2,
            max_tokens=900,
        )

    def _format_rag_context_for_prompt(self, rag_result: dict) -> str:
        chunks = rag_result.get("chunks", [])

        if not chunks:
            return "No se recuperó contexto documental relevante."

        return "\n".join(
            f"- Fuente: {chunk.get('source')} | Score: {chunk.get('score')}\n"
            f"  {chunk.get('text', '')[:900]}"
            for chunk in chunks
        )

    def _format_analytics_for_prompt(
        self,
        analytics_result: dict | None,
    ) -> str:
        if analytics_result is None:
            return "No se ejecutó consulta analítica."

        if not analytics_result.get("success"):
            return (
                "No fue posible ejecutar la consulta analítica: "
                f"{analytics_result.get('error')}"
            )

        return (
            f"SQL ejecutado:\n{analytics_result.get('sql')}\n\n"
            f"Datos obtenidos:\n{analytics_result.get('data')}"
        )

    def _compose_local_executive_answer(
        self,
        question: str,
        rag_result: dict,
        analytics_result: dict | None,
    ) -> str:
        analytics_summary = self._build_analytics_summary(analytics_result)
        context_insights = self._build_context_insights(rag_result)
        sources_summary = self._format_sources_summary(rag_result)

        answer = (
            "## Respuesta ejecutiva\n\n"
            f"**Consulta analizada:** {question}\n\n"
            f"{analytics_summary['direct_answer']}\n\n"
            "### Interpretación de negocio\n\n"
            f"{analytics_summary['business_interpretation']}\n\n"
            "### Evidencia numérica\n\n"
            f"{analytics_summary['numeric_evidence']}\n\n"
            "### Lectura con base en el contexto documental\n\n"
            f"{context_insights}\n\n"
            "### Recomendación ejecutiva\n\n"
            f"{analytics_summary['recommendation']}\n\n"
            "### Fuentes consultadas\n\n"
            f"{sources_summary}\n\n"
            "### Limitaciones\n\n"
            "Esta respuesta se genera con el corpus documental y los datos estructurados disponibles en el entorno local. "
            "Para una respuesta generativa completa con razonamiento de modelo, se debe activar Amazon Bedrock mediante "
            "`USE_BEDROCK=true` y credenciales AWS válidas."
        )

        return answer

    def _build_analytics_summary(
        self,
        analytics_result: dict | None,
    ) -> dict:
        default_summary = {
            "direct_answer": (
                "Con la información disponible, la consulta se responde principalmente a partir del contexto documental recuperado."
            ),
            "business_interpretation": (
                "El análisis debe interpretarse como una lectura conceptual, ya que no se ejecutó una consulta estructurada de datos para esta pregunta."
            ),
            "numeric_evidence": (
                "No hay evidencia numérica estructurada asociada a esta consulta."
            ),
            "recommendation": (
                "Se recomienda complementar la consulta con datos estructurados si se requiere una conclusión cuantitativa o comparativa."
            ),
        }

        if analytics_result is None:
            return default_summary

        if not analytics_result.get("success"):
            return {
                "direct_answer": (
                    "No fue posible completar la parte analítica estructurada de la consulta."
                ),
                "business_interpretation": (
                    "La interpretación debe hacerse con cautela porque la consulta a datos no se ejecutó correctamente."
                ),
                "numeric_evidence": (
                    f"Error reportado por la herramienta analítica: {analytics_result.get('error')}"
                ),
                "recommendation": (
                    "Se recomienda revisar la disponibilidad del archivo Parquet, la estructura de columnas y la consulta generada."
                ),
            }

        data = analytics_result.get("data", [])

        if not data:
            return {
                "direct_answer": (
                    "La consulta analítica se ejecutó correctamente, pero no retornó registros."
                ),
                "business_interpretation": (
                    "No es posible establecer una conclusión de negocio sin registros en el resultado."
                ),
                "numeric_evidence": (
                    "La herramienta analítica no retornó datos para resumir."
                ),
                "recommendation": (
                    "Se recomienda validar filtros, periodo de análisis y disponibilidad de datos."
                ),
            }

        first_row = data[0]

        if "regional" in first_row and "promedio_indicador" in first_row:
            ordered = sorted(
                data,
                key=lambda row: float(row.get("promedio_indicador", 0)),
                reverse=True,
            )

            highest = ordered[0]
            lowest = ordered[-1]

            highest_value = float(highest.get("promedio_indicador", 0))
            lowest_value = float(lowest.get("promedio_indicador", 0))
            gap = round(highest_value - lowest_value, 2)

            table_rows = [
                "| Regional | Registros | Promedio del indicador |",
                "|---|---:|---:|",
            ]

            for row in ordered:
                table_rows.append(
                    f"| {row.get('regional')} | "
                    f"{row.get('total_registros', 'N/A')} | "
                    f"{row.get('promedio_indicador', 'N/A')} |"
                )

            if gap >= 3:
                interpretation = (
                    f"La diferencia entre la regional con mayor promedio y la de menor promedio es de **{gap} puntos**. "
                    "Esta brecha es relevante y debería revisarse como una posible alerta de desempeño, especialmente si se mantiene en varios periodos."
                )
            else:
                interpretation = (
                    f"La diferencia entre regionales es de **{gap} puntos**. "
                    "La brecha no parece crítica en una primera lectura, aunque debe revisarse junto con la tendencia histórica."
                )

            return {
                "direct_answer": (
                    f"El análisis muestra que **{highest.get('regional')}** tiene el promedio más alto del indicador "
                    f"con **{highest_value}**, mientras que **{lowest.get('regional')}** presenta el promedio más bajo "
                    f"con **{lowest_value}**."
                ),
                "business_interpretation": interpretation,
                "numeric_evidence": "\n".join(table_rows),
                "recommendation": (
                    "Se recomienda revisar la regional con mayor promedio para identificar si el comportamiento responde a mayor presión operativa, "
                    "incremento de costos, cambios en la población analizada o diferencias en la gestión territorial."
                ),
            }

        if "promedio_indicador" in first_row:
            promedio = first_row.get("promedio_indicador")
            minimo = first_row.get("minimo")
            maximo = first_row.get("maximo")
            total = first_row.get("total_registros")

            return {
                "direct_answer": (
                    f"El indicador presenta un promedio general de **{promedio}** sobre **{total} registros**."
                ),
                "business_interpretation": (
                    "Este resultado permite tener una lectura agregada del comportamiento del indicador, pero no permite identificar diferencias por regional o periodo."
                ),
                "numeric_evidence": (
                    f"- Total de registros: **{total}**\n"
                    f"- Promedio: **{promedio}**\n"
                    f"- Mínimo: **{minimo}**\n"
                    f"- Máximo: **{maximo}**"
                ),
                "recommendation": (
                    "Se recomienda complementar este resultado con cortes por regional, mes o segmento para identificar patrones más accionables."
                ),
            }

        return {
            "direct_answer": (
                "La consulta analítica se ejecutó correctamente y retornó datos estructurados."
            ),
            "business_interpretation": (
                "El resultado debe interpretarse según las columnas disponibles y el objetivo de la consulta."
            ),
            "numeric_evidence": (
                f"Datos retornados: `{data}`"
            ),
            "recommendation": (
                "Se recomienda revisar si el resultado responde exactamente a la pregunta de negocio o si requiere mayor segmentación."
            ),
        }

    def _build_context_insights(self, rag_result: dict) -> str:
        chunks = rag_result.get("chunks", [])

        if not chunks:
            return (
                "No se recuperaron fragmentos documentales suficientemente relevantes para complementar la interpretación."
            )

        corpus_text = " ".join(
            chunk.get("text", "")
            for chunk in chunks
        ).lower()

        insights = []

        if "siniestralidad" in corpus_text:
            insights.append(
                "La siniestralidad se interpreta como un indicador crítico para evaluar la relación entre costos, reclamaciones, atenciones o beneficios frente a los recursos disponibles."
            )

        if "70 y 80" in corpus_text or "70 a 80" in corpus_text:
            insights.append(
                "El contexto documental sugiere que valores entre 70 y 80 requieren seguimiento, porque pueden reflejar incremento de costos o mayor uso de servicios."
            )

        if "3 puntos" in corpus_text:
            insights.append(
                "El corpus indica que una diferencia superior a 3 puntos entre regionales puede considerarse una alerta de desempeño si se sostiene en el tiempo."
            )

        if "tendencia mensual" in corpus_text:
            insights.append(
                "La interpretación no debería basarse en un único dato aislado; conviene revisar tendencia mensual, volumen de registros y condiciones particulares de cada territorio."
            )

        if not insights:
            best_chunk = chunks[0]
            text = best_chunk.get("text", "").strip()

            if len(text) > 500:
                text = text[:500] + "..."

            insights.append(
                f"El fragmento documental más relevante aporta contexto para interpretar la consulta: {text}"
            )

        return "\n".join(f"- {insight}" for insight in insights)

    def _format_sources_summary(self, rag_result: dict) -> str:
        chunks = rag_result.get("chunks", [])

        if not chunks:
            return "No se registraron fuentes documentales para esta respuesta."

        seen_sources = []

        for chunk in chunks:
            source = chunk.get("source")

            if source and source not in seen_sources:
                seen_sources.append(source)

        return "\n".join(f"- {source}" for source in seen_sources)