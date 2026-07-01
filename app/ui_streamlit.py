import io
import json
import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/chat")
METRICS_PATH = Path("data/metrics.jsonl")


# Paleta visual inspirada en Universidad EAN:
# verde institucional como acento + neutros ejecutivos.
EAN_GREEN = "#78BE20"
EAN_GREEN_DARK = "#4F8A10"
EAN_GREEN_SOFT = "#EAF6DA"
EAN_GREEN_LIGHT = "#F5FAED"

TEXT = "#111827"
TEXT_SOFT = "#6B7280"
TEXT_MUTED = "#9CA3AF"

BG = "#F7F9F7"
WHITE = "#FFFFFF"
BORDER = "#E5E7EB"
CARD_SHADOW = "0 8px 22px rgba(17, 24, 39, 0.05)"


st.set_page_config(
    page_title="Panel Ejecutivo de Analítica",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {BG};
                color: {TEXT};
            }}

            .block-container {{
                max-width: 1280px;
                padding-top: 1rem;
                padding-bottom: 2.5rem;
            }}

            [data-testid="stSidebar"] {{
                background-color: {WHITE};
                border-right: 1px solid {BORDER};
            }}

            .hero {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-left: 7px solid {EAN_GREEN};
                border-radius: 20px;
                padding: 1.35rem 1.5rem;
                margin-bottom: 1rem;
                box-shadow: {CARD_SHADOW};
            }}

            .hero-kicker {{
                font-size: 0.78rem;
                font-weight: 850;
                color: {EAN_GREEN_DARK};
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.35rem;
            }}

            .hero-title {{
                font-size: 2.05rem;
                font-weight: 850;
                color: {TEXT};
                margin-bottom: 0.22rem;
            }}

            .hero-subtitle {{
                font-size: 0.98rem;
                color: {TEXT_SOFT};
                margin-bottom: 0;
                max-width: 880px;
            }}

            .section-card {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 18px;
                padding: 1rem 1.15rem;
                margin-bottom: 1rem;
                box-shadow: {CARD_SHADOW};
            }}

            .section-title {{
                font-size: 1.05rem;
                font-weight: 850;
                color: {TEXT};
                margin-bottom: 0.18rem;
            }}

            .section-caption {{
                font-size: 0.92rem;
                color: {TEXT_SOFT};
                margin-bottom: 0;
            }}

            .executive-strip {{
                background: linear-gradient(90deg, {EAN_GREEN_SOFT} 0%, #FFFFFF 100%);
                border: 1px solid #D3EAB8;
                border-radius: 18px;
                padding: 1rem 1.1rem;
                margin-bottom: 1rem;
                box-shadow: 0 5px 16px rgba(17, 24, 39, 0.04);
            }}

            .executive-strip-label {{
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: {EAN_GREEN_DARK};
                font-weight: 850;
                margin-bottom: 0.2rem;
            }}

            .executive-strip-value {{
                font-size: 1.25rem;
                color: {TEXT};
                font-weight: 850;
                margin-bottom: 0;
            }}

            .architecture-note {{
                background: {EAN_GREEN_LIGHT};
                border: 1px solid #D3EAB8;
                border-radius: 16px;
                padding: 0.95rem 1rem;
                margin-bottom: 1rem;
            }}

            div.stButton > button:first-child {{
                background-color: {EAN_GREEN};
                color: white;
                border: 1px solid {EAN_GREEN};
                border-radius: 12px;
                font-weight: 850;
                padding: 0.65rem 1rem;
            }}

            div.stButton > button:first-child:hover {{
                background-color: {EAN_GREEN_DARK};
                border-color: {EAN_GREEN_DARK};
                color: white;
            }}

            .stTextArea textarea {{
                border-radius: 14px;
                border: 1px solid {BORDER};
                background: {WHITE};
            }}

            .stSelectbox div[data-baseweb="select"] > div {{
                border-radius: 12px;
                border-color: {BORDER};
            }}

            [data-testid="stMetric"] {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 18px;
                padding: 1rem;
                box-shadow: {CARD_SHADOW};
            }}

            [data-testid="stMetricLabel"] {{
                color: {TEXT_SOFT};
                font-weight: 750;
            }}

            [data-testid="stMetricValue"] {{
                color: {TEXT};
                font-weight: 850;
            }}

            [data-testid="stMetricDelta"] {{
                font-weight: 750;
            }}

            [data-baseweb="tab-list"] {{
                gap: 0.5rem;
                border-bottom: none;
                margin-bottom: 0.65rem;
            }}

            [data-baseweb="tab"] {{
                background-color: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 999px;
                padding: 0.42rem 1.05rem;
                color: {TEXT};
                font-weight: 750;
            }}

            [aria-selected="true"] {{
                background-color: {EAN_GREEN_SOFT} !important;
                border-color: {EAN_GREEN} !important;
                color: {EAN_GREEN_DARK} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def read_metrics() -> pd.DataFrame:
    if not METRICS_PATH.exists():
        return pd.DataFrame()

    rows = []

    with open(METRICS_PATH, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    return df


def find_pdf_path(tool_calls: list[dict]) -> str | None:
    for call in tool_calls:
        if call.get("tool_name") == "pdf_report_generator":
            output = call.get("output", {})

            if output.get("success"):
                return output.get("file_path")

    return None


def ensure_pdf_requested(question: str) -> str:
    pdf_keywords = [
        "pdf",
        "reporte",
        "informe",
        "descargar",
        "documento",
    ]

    question_lower = question.lower()

    if any(keyword in question_lower for keyword in pdf_keywords):
        return question

    return f"{question.strip()} y genera un reporte PDF"


def as_percent(value: float | int | None) -> str:
    if value is None:
        return "N/A"

    return f"{round(float(value) * 100, 2)}%"


def as_seconds(value: float | int | None) -> str:
    if value is None:
        return "N/A"

    return f"{round(float(value), 4)} s"


def as_money(value: float | int | None) -> str:
    if value is None:
        return "N/A"

    return f"USD {round(float(value), 6)}"


def as_number(value: float | int | None) -> str:
    if value is None:
        return "N/A"

    return str(round(float(value), 2))


def evaluate_kpi(
    value: float | int | None,
    threshold: float | int,
    direction: str,
) -> str:
    if value is None:
        return "Sin dato"

    value = float(value)
    threshold = float(threshold)

    if direction == "gte":
        return "Cumple" if value >= threshold else "Revisar"

    return "Cumple" if value <= threshold else "Revisar"


def status_label(status: str) -> tuple[str, str]:
    if status == "Cumple":
        return "Cumple", "normal"

    if status == "Revisar":
        return "Revisar", "inverse"

    if status == "Monitoreo":
        return "Monitoreo", "off"

    return "Sin dato", "off"


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Analítica ejecutiva</div>
            <div class="hero-title">Panel Ejecutivo de Analítica</div>
            <p class="hero-subtitle">
                Consulta indicadores, evalúa el desempeño del sistema y genera reportes ejecutivos con una experiencia clara y trazable.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(title: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">{title}</div>
            <p class="section-caption">{caption}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_executive_summary(df_metrics: pd.DataFrame) -> None:
    if df_metrics.empty:
        st.markdown(
            """
            <div class="executive-strip">
                <div class="executive-strip-label">Estado del panel</div>
                <p class="executive-strip-value">Sin consultas registradas</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    latest = df_metrics.iloc[-1]

    checks = [
        evaluate_kpi(
            latest.get("tool_success_rate", 0),
            latest.get("threshold_tool_success_rate", 0.95),
            "gte",
        ),
        evaluate_kpi(
            latest.get("judge_score", 0),
            latest.get("threshold_judge_score", 7.5),
            "gte",
        ),
        evaluate_kpi(
            latest.get("ttl_seconds", 0),
            latest.get("threshold_ttl_seconds", 10),
            "lte",
        ),
        evaluate_kpi(
            latest.get("estimated_cost_usd", 0),
            latest.get("threshold_cost_usd", 0.05),
            "lte",
        ),
        evaluate_kpi(
            latest.get("calculation_error_rate", 0),
            latest.get("threshold_calculation_error_rate", 0.03),
            "lte",
        ),
        evaluate_kpi(
            latest.get("rag_latency_seconds", 0),
            latest.get("threshold_rag_latency_seconds", 2),
            "lte",
        ),
        evaluate_kpi(
            latest.get("rag_corpus_coverage", 0),
            latest.get("threshold_rag_corpus_coverage", 0.85),
            "gte",
        ),
    ]

    total_ok = sum(1 for item in checks if item == "Cumple")
    state = "Operación estable" if total_ok >= 6 else "Requiere revisión"

    st.markdown(
        f"""
        <div class="executive-strip">
            <div class="executive-strip-label">Estado general</div>
            <p class="executive-strip-value">{state} · {total_ok}/7 indicadores cumplen los umbrales</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_line_chart(
    df: pd.DataFrame,
    y_column: str,
    title: str,
    threshold: float | None = None,
    y_title: str = "",
) -> go.Figure:
    fig = go.Figure()

    if df.empty or y_column not in df.columns:
        fig.update_layout(
            title=title,
            paper_bgcolor=WHITE,
            plot_bgcolor=WHITE,
            height=320,
            margin=dict(l=20, r=20, t=50, b=20),
        )
        return fig

    chart_df = df.copy()

    fig.add_trace(
        go.Scatter(
            x=chart_df["timestamp"],
            y=chart_df[y_column],
            mode="lines+markers",
            line=dict(color=EAN_GREEN, width=3),
            marker=dict(size=7, color=EAN_GREEN_DARK),
            fill="tozeroy",
            fillcolor="rgba(120, 190, 32, 0.12)",
            hovertemplate="%{y}<extra></extra>",
        )
    )

    if threshold is not None:
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color="#9CA3AF",
            annotation_text=f"Umbral {threshold}",
            annotation_position="top right",
        )

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=TEXT)),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
        font=dict(color=TEXT),
        xaxis_title="",
        yaxis_title=y_title,
    )

    fig.update_xaxes(showgrid=False, linecolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER, zeroline=False)

    return fig


def build_compliance_chart(latest: pd.Series) -> go.Figure:
    labels = [
        "Ejecución",
        "Calidad",
        "Cobertura",
        "Velocidad",
    ]

    tool_value = float(latest.get("tool_success_rate", 0)) * 100
    judge_value = float(latest.get("judge_score", 0)) * 10
    coverage_value = float(latest.get("rag_corpus_coverage", 0)) * 100

    rag_latency = float(latest.get("rag_latency_seconds", 0))
    rag_threshold = max(float(latest.get("threshold_rag_latency_seconds", 2)), 0.01)
    speed_value = max(0, 100 - ((rag_latency / rag_threshold) * 100))

    values = [
        tool_value,
        judge_value,
        coverage_value,
        speed_value,
    ]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker_color=[
                EAN_GREEN,
                EAN_GREEN_DARK,
                "#9FCC53",
                "#C2DF93",
            ],
            text=[f"{round(value, 1)}%" for value in values],
            textposition="outside",
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text="Cumplimiento ejecutivo", font=dict(size=16, color=TEXT)),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        height=330,
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(color=TEXT),
        yaxis_title="Nivel de cumplimiento",
        xaxis_title="",
        showlegend=False,
    )

    fig.update_yaxes(range=[0, 110], gridcolor=BORDER, zeroline=False)
    fig.update_xaxes(showgrid=False)

    return fig


def tool_status_list(tool_calls: list[dict]) -> str:
    labels = {
        "rag_search": "Recuperación documental",
        "duckdb_analytics": "Análisis de datos",
        "kpi_calculator": "Cálculo de indicadores",
        "pdf_report_generator": "Reporte PDF",
    }

    if not tool_calls:
        return "Sin componentes registrados."

    result = []

    for call in tool_calls:
        label = labels.get(call.get("tool_name", "tool"), call.get("tool_name", "tool"))
        success = call.get("success", False)
        result.append(f"{label}: {'OK' if success else 'ERROR'}")

    return " · ".join(result)


def run_query(question: str) -> dict:
    response = requests.post(
        API_URL,
        json={"question": question},
        timeout=60,
    )
    response.raise_for_status()

    return response.json()


def download_metrics_csv(df_metrics: pd.DataFrame) -> bytes:
    buffer = io.StringIO()
    df_metrics.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def render_architecture_diagram() -> None:
    architecture_dot = """
    digraph {
        graph [
            rankdir=LR,
            bgcolor="transparent",
            pad="0.4",
            nodesep="0.65",
            ranksep="0.85"
        ]

        node [
            shape=rect,
            style="rounded,filled",
            fontname="Arial",
            fontsize=11,
            color="#D1D5DB",
            fillcolor="#FFFFFF",
            fontcolor="#111827",
            margin="0.16,0.10"
        ]

        edge [
            color="#6B7280",
            arrowsize=0.8,
            fontname="Arial",
            fontsize=10
        ]

        user [
            label="Usuario\\nconsulta ejecutiva",
            fillcolor="#EAF6DA",
            color="#78BE20"
        ]

        ui [
            label="Interfaz\\nStreamlit"
        ]

        api [
            label="Backend\\nFastAPI"
        ]

        orchestrator [
            label="Agente\\nOrquestador",
            fillcolor="#EAF6DA",
            color="#78BE20"
        ]

        rag [
            label="Recuperación\\ndocumental"
        ]

        analytics [
            label="Análisis\\nDuckDB + Parquet"
        ]

        kpi [
            label="Cálculo\\nKPI"
        ]

        pdf [
            label="Reporte\\nPDF"
        ]

        judge [
            label="Validación\\nde respuesta"
        ]

        metrics [
            label="Observabilidad\\n8 KPIs"
        ]

        docs [
            label="Corpus\\ndocumental",
            shape=cylinder,
            fillcolor="#F9FAFB"
        ]

        parquet [
            label="Datos\\nParquet",
            shape=cylinder,
            fillcolor="#F9FAFB"
        ]

        reports [
            label="Reportes\\ngenerados",
            fillcolor="#F9FAFB"
        ]

        aws [
            label="Ruta AWS objetivo\\nBedrock · S3 · OpenSearch · CloudWatch",
            fillcolor="#F3F4F6",
            color="#9CA3AF"
        ]

        user -> ui
        ui -> api
        api -> orchestrator

        orchestrator -> rag
        orchestrator -> analytics
        orchestrator -> kpi
        orchestrator -> pdf
        orchestrator -> judge
        orchestrator -> metrics

        docs -> rag
        parquet -> analytics
        pdf -> reports

        rag -> judge
        analytics -> judge
        kpi -> judge
        judge -> metrics

        orchestrator -> aws [style=dashed, label="evolución cloud"]
    }
    """

    st.graphviz_chart(architecture_dot, use_container_width=True)


inject_css()
render_hero()

df_metrics = read_metrics()
latest = df_metrics.iloc[-1] if not df_metrics.empty else None


tab_query, tab_dashboard, tab_architecture = st.tabs(
    ["Consulta", "Dashboard", "Arquitectura"]
)


with tab_query:
    render_section(
        "Consulta ejecutiva",
        "Realiza una pregunta de negocio y recibe una respuesta trazable, con soporte documental y opción de reporte.",
    )

    if "last_result" not in st.session_state:
        st.session_state["last_result"] = None

    if "last_question" not in st.session_state:
        st.session_state["last_question"] = ""

    examples = [
        "Compara el promedio del indicador de siniestralidad por regional",
        "¿Qué significa una siniestralidad alta y cómo debería interpretarse?",
        "¿Cuándo una brecha entre regionales debería considerarse una alerta?",
        "¿Qué métricas de observabilidad usa este sistema?",
    ]

    left, right = st.columns([2.25, 1])

    with left:
        selected_example = st.selectbox("Consulta sugerida", examples)

        question = st.text_area(
            "Pregunta",
            value=selected_example,
            height=110,
            placeholder="Escribe aquí tu consulta...",
        )

        generate_pdf = st.checkbox(
            "Generar reporte PDF",
            value=True,
            help="Si está activado, el sistema generará un reporte descargable junto con la respuesta.",
        )

        run_button = st.button(
            "Ejecutar análisis",
            type="primary",
            use_container_width=True,
        )

    with right:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Recomendación para demo</div>
                <p class="section-caption">
                    Usa una consulta de comparación por regional para mostrar análisis de datos, validación y reporte.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if run_button:
        if not question.strip():
            st.warning("Escribe una pregunta antes de ejecutar.")
        else:
            backend_question = (
                ensure_pdf_requested(question)
                if generate_pdf
                else question
            )

            with st.spinner("Procesando consulta..."):
                try:
                    result = run_query(backend_question)
                except requests.RequestException as exc:
                    st.error(f"No fue posible consultar el backend: {exc}")
                    st.stop()

            st.session_state["last_result"] = result
            st.session_state["last_question"] = question

            st.success("Análisis ejecutado correctamente.")

    result = st.session_state.get("last_result")

    if result:
        metrics = result.get("metrics", {})
        tool_calls = result.get("tool_calls", [])

        st.markdown("### Resumen de la consulta")

        query_kpis = st.columns(4)

        query_kpis[0].metric(
            "Componentes usados",
            metrics.get("tools_total", 0),
        )

        query_kpis[1].metric(
            "Éxito",
            as_percent(metrics.get("tool_success_rate", 0)),
        )

        query_kpis[2].metric(
            "Calidad",
            f"{as_number(metrics.get('judge_score', 0))}/10",
        )

        query_kpis[3].metric(
            "Tiempo",
            as_seconds(metrics.get("ttl_seconds", 0)),
        )

        st.markdown("### Resultado")

        with st.container(border=True):
            st.markdown(result.get("answer", ""))

        st.markdown("### Acciones")

        pdf_path = find_pdf_path(tool_calls)

        action_cols = st.columns([1.1, 1.1, 2])

        with action_cols[0]:
            if pdf_path and Path(pdf_path).exists():
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Descargar PDF",
                        data=pdf_file,
                        file_name=Path(pdf_path).name,
                        mime="application/pdf",
                        use_container_width=True,
                    )
            else:
                st.button(
                    "PDF no disponible",
                    disabled=True,
                    use_container_width=True,
                )

        with action_cols[1]:
            if st.button("Limpiar resultado", use_container_width=True):
                st.session_state["last_result"] = None
                st.session_state["last_question"] = ""
                st.rerun()

        if not pdf_path:
            st.caption(
                "No se generó un PDF para esta consulta. Activa la opción de reporte o incluye la palabra PDF, reporte o informe en la pregunta."
            )

        st.markdown("### Componentes utilizados")
        st.info(tool_status_list(tool_calls))

        with st.expander("Ver soporte técnico"):
            detail_cols = st.columns(2)

            with detail_cols[0]:
                st.markdown("**Fuentes consultadas**")
                sources = result.get("sources", [])

                if sources:
                    for source in sources:
                        st.markdown(f"- {source}")
                else:
                    st.caption("No se registraron fuentes.")

                st.markdown("**Validación**")
                st.json(result.get("judge", {}))

            with detail_cols[1]:
                st.markdown("**Ejecución interna**")
                st.json(tool_calls)

                st.markdown("**Métricas de la consulta**")
                st.json(metrics)


with tab_dashboard:
    render_executive_summary(df_metrics)

    render_section(
        "Dashboard ejecutivo",
        "Seguimiento visual de calidad, oportunidad, cobertura documental, costo y consumo estimado.",
    )

    if latest is None:
        st.info("Aún no hay datos suficientes. Ejecuta una consulta para poblar el panel.")
    else:
        status_tools, color_tools = status_label(
            evaluate_kpi(
                latest.get("tool_success_rate", 0),
                latest.get("threshold_tool_success_rate", 0.95),
                "gte",
            )
        )
        status_judge, color_judge = status_label(
            evaluate_kpi(
                latest.get("judge_score", 0),
                latest.get("threshold_judge_score", 7.5),
                "gte",
            )
        )
        status_ttl, color_ttl = status_label(
            evaluate_kpi(
                latest.get("ttl_seconds", 0),
                latest.get("threshold_ttl_seconds", 10),
                "lte",
            )
        )
        status_cost, color_cost = status_label(
            evaluate_kpi(
                latest.get("estimated_cost_usd", 0),
                latest.get("threshold_cost_usd", 0.05),
                "lte",
            )
        )

        top_row = st.columns(4)
        top_row[0].metric(
            "Éxito de ejecución",
            as_percent(latest.get("tool_success_rate", 0)),
            status_tools,
            delta_color=color_tools,
        )
        top_row[1].metric(
            "Calidad de respuesta",
            f"{as_number(latest.get('judge_score', 0))}/10",
            status_judge,
            delta_color=color_judge,
        )
        top_row[2].metric(
            "Tiempo total",
            as_seconds(latest.get("ttl_seconds", 0)),
            status_ttl,
            delta_color=color_ttl,
        )
        top_row[3].metric(
            "Costo estimado",
            as_money(latest.get("estimated_cost_usd", 0)),
            status_cost,
            delta_color=color_cost,
        )

        second_row = st.columns(4)
        second_row[0].metric(
            "Error en cálculos",
            as_percent(latest.get("calculation_error_rate", 0)),
        )
        second_row[1].metric(
            "Latencia documental",
            as_seconds(latest.get("rag_latency_seconds", 0)),
        )
        second_row[2].metric(
            "Cobertura documental",
            as_percent(latest.get("rag_corpus_coverage", 0)),
        )
        second_row[3].metric(
            "Consumo estimado",
            as_number(latest.get("avg_tokens_per_session", 0)),
        )

        st.markdown("### Tendencias principales")

        chart_cols = st.columns(2)

        with chart_cols[0]:
            fig_ttl = build_line_chart(
                df_metrics,
                y_column="ttl_seconds",
                title="Tiempo de respuesta",
                threshold=float(latest.get("threshold_ttl_seconds", 10)),
                y_title="Segundos",
            )
            st.plotly_chart(fig_ttl, use_container_width=True)

        with chart_cols[1]:
            fig_judge = build_line_chart(
                df_metrics,
                y_column="judge_score",
                title="Calidad de respuesta",
                threshold=float(latest.get("threshold_judge_score", 7.5)),
                y_title="Puntaje",
            )
            st.plotly_chart(fig_judge, use_container_width=True)

        st.markdown("### Cumplimiento actual")

        fig_compliance = build_compliance_chart(latest)
        st.plotly_chart(fig_compliance, use_container_width=True)

        with st.expander("Histórico descargable"):
            st.caption(
                "El registro completo se mantiene oculto para conservar una vista ejecutiva limpia."
            )
            st.download_button(
                label="Descargar histórico en CSV",
                data=download_metrics_csv(df_metrics),
                file_name="historico_metricas.csv",
                mime="text/csv",
            )


with tab_architecture:
    render_section(
        "Arquitectura de solución",
        "Vista ejecutiva del flujo funcional y su evolución propuesta hacia AWS.",
    )

    with st.container(border=True):
        render_architecture_diagram()

    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        with st.container(border=True):
            st.markdown("### Lectura del flujo")
            st.markdown(
                """
                El usuario realiza una consulta desde la interfaz. El backend recibe la solicitud y el orquestador coordina los componentes necesarios: recuperación documental, análisis estructurado, cálculo de indicadores, generación de reportes, validación de respuesta y registro de métricas.
                """
            )

    with col_b:
        with st.container(border=True):
            st.markdown("### Componentes principales")
            st.markdown(
                """
                - Interfaz ejecutiva  
                - API de consulta  
                - Agente orquestador  
                - Recuperación documental  
                - Análisis con DuckDB  
                - Cálculo KPI  
                - Generación PDF  
                - Validación de respuesta  
                - Observabilidad  
                """
            )

        with st.container(border=True):
            st.markdown("### Ruta AWS")
            st.markdown(
                """
                - Amazon Bedrock  
                - Amazon S3  
                - OpenSearch o pgvector  
                - ECS Fargate o EC2  
                - CloudWatch  
                """
            )