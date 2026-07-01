# Sistema Agéntico Analítico con LLM + RAG + Tools

Prototipo técnico desarrollado en Python para la prueba de **Python Developer / Data Analyst con IA**.
El sistema implementa un flujo agéntico completo que integra recuperación documental tipo RAG, herramientas analíticas, generación de reportes, evaluación mediante agente juez y observabilidad de KPIs.

El dominio elegido es un **motor analítico conversacional para indicadores financieros y de desempeño**, orientado a escenarios de compensación, aseguramiento o gestión organizacional.

---

## 1. Descripción general

Este proyecto permite que un usuario realice preguntas en lenguaje natural sobre indicadores de desempeño, siniestralidad, regionales, KPIs y reportes ejecutivos.

El sistema recibe la consulta, recupera contexto documental, ejecuta herramientas analíticas sobre datos estructurados, calcula KPIs relevantes, genera reportes PDF cuando se solicita y valida la respuesta mediante un agente juez.

Flujo principal:

```text
Usuario
→ Interfaz Streamlit
→ Backend FastAPI
→ Agente Orquestador
→ Worker RAG
→ Tools analíticas
→ Agente juez
→ Métricas de observabilidad
→ Respuesta final
```

---

## 2. Objetivo del sistema

El objetivo es demostrar una arquitectura funcional de IA generativa aplicada a analítica de datos, integrando:

* Un agente orquestador.
* Subcomponentes especializados.
* RAG sobre corpus documental.
* Tools externas.
* Consulta analítica con DuckDB sobre archivos Parquet.
* Cálculo de KPIs.
* Generación de reportes PDF.
* Agente juez evaluador.
* Observabilidad con KPIs técnicos y de negocio.
* Preparación para despliegue en AWS.

---

## 3. Stack tecnológico

| Componente                     | Tecnología                                  |
| ------------------------------ | ------------------------------------------- |
| Lenguaje                       | Python 3.12+                                |
| Backend                        | FastAPI                                     |
| Frontend                       | Streamlit                                   |
| RAG local                      | TF-IDF + cosine similarity con scikit-learn |
| Lectura documental             | pypdf + archivos TXT                        |
| Datos estructurados            | Parquet                                     |
| Motor analítico                | DuckDB                                      |
| Reportes                       | ReportLab                                   |
| LLM productivo propuesto       | Amazon Bedrock                              |
| Modelo principal propuesto     | Claude 3 Haiku                              |
| Modelo fallback propuesto      | Claude 3 Sonnet                             |
| Observabilidad local           | JSONL + dashboard Streamlit                 |
| Observabilidad cloud propuesta | Amazon CloudWatch                           |
| Despliegue propuesto           | Docker + ECS Fargate o EC2                  |

---

## 4. Arquitectura implementada

El sistema se organiza en módulos separados para facilitar mantenimiento, evaluación y despliegue.

```text
agentic-analytics-rag/
│
├── app/
│   ├── main.py
│   ├── ui_streamlit.py
│   ├── config.py
│   └── schemas.py
│
├── orchestrator/
│   └── agent_orchestrator.py
│
├── workers/
│   ├── rag_worker.py
│   ├── analytics_worker.py
│   └── report_worker.py
│
├── rag/
│   └── local_retriever.py
│
├── tools/
│   ├── duckdb_tool.py
│   ├── kpi_calculator.py
│   └── pdf_generator.py
│
├── judge/
│   └── judge_llm.py
│
├── llm/
│   └── bedrock_client.py
│
├── observability/
│   └── metrics.py
│
├── data/
│   ├── documents/
│   ├── parquet/
│   └── reports/
│
├── docs/
│
├── tests/
│
├── requirements.txt
├── .env
└── README.md
```

---

## 5. Componentes principales

### 5.1 Agente orquestador

El orquestador es el componente central del sistema. Recibe la pregunta del usuario y decide qué capacidades activar.

Responsabilidades:

* Recibir la consulta.
* Ejecutar recuperación RAG.
* Activar la tool analítica cuando la pregunta requiere datos.
* Activar la calculadora de KPIs cuando hay resultados numéricos.
* Generar PDF cuando el usuario lo solicita.
* Componer la respuesta.
* Enviar la respuesta al agente juez.
* Registrar métricas de observabilidad.

Archivo principal:

```text
orchestrator/agent_orchestrator.py
```

---

### 5.2 Worker RAG

El worker RAG recupera información relevante desde el corpus documental ubicado en:

```text
data/documents/
```

En el MVP local se usa:

* Lectura de TXT/PDF.
* División de texto en chunks.
* Vectorización TF-IDF.
* Similitud coseno.
* Ranking de fragmentos.
* Normalización del score para calcular cobertura RAG.

Archivo principal:

```text
rag/local_retriever.py
```

En una versión productiva AWS, este componente puede migrarse a:

* Amazon Titan Embeddings v2.
* Amazon OpenSearch Serverless.
* pgvector en Amazon RDS.
* Amazon S3 como almacenamiento documental.

---

### 5.3 Tool DuckDB Analytics

Herramienta analítica encargada de consultar datos estructurados en formato Parquet.

Archivo principal:

```text
tools/duckdb_tool.py
```

Ejemplo de consulta soportada:

```text
Compara el promedio del indicador de siniestralidad por regional
```

La tool ejecuta SQL sobre:

```text
data/parquet/indicadores.parquet
```

Ejemplo de resultado:

```text
Regional Bogotá: promedio 72.63
Regional Antioquia: promedio 68.27
```

---

### 5.4 Tool KPI Calculator

Herramienta encargada de calcular brechas, diferencias o variaciones sobre los resultados analíticos.

Archivo principal:

```text
tools/kpi_calculator.py
```

Ejemplo:

```text
Diferencia absoluta entre Bogotá y Antioquia: 4.36 puntos
Valor más alto: Bogotá
```

---

### 5.5 Tool PDF Generator

Herramienta encargada de generar reportes PDF cuando el usuario lo solicita.

Archivo principal:

```text
tools/pdf_generator.py
```

Los reportes se guardan en:

```text
data/reports/
```

Ejemplo de consulta:

```text
Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF
```

---

### 5.6 Agente juez

El agente juez evalúa la respuesta generada antes de entregarla al usuario.

Criterios evaluados:

* Relevancia frente a la pregunta.
* Uso del contexto RAG.
* Precisión numérica.
* Riesgo de alucinación.
* Claridad de la respuesta.

Archivo principal:

```text
judge/judge_llm.py
```

El sistema funciona con dos modos:

```text
USE_BEDROCK=false
→ Juez heurístico local

USE_BEDROCK=true
→ Judge LLM usando Amazon Bedrock
```

---

### 5.7 Capa LLM con Amazon Bedrock

El sistema incluye una capa preparada para conectarse a Amazon Bedrock.

Archivo principal:

```text
llm/bedrock_client.py
```

Modo actual del MVP:

```text
USE_BEDROCK=false
```

Esto permite ejecutar el sistema localmente sin credenciales AWS ni costos.
Cuando se activa Bedrock, el sistema puede usar modelos como:

* Claude 3 Haiku.
* Claude 3 Sonnet.
* Llama 3.
* Titan Text.

---

## 6. Observabilidad

El sistema registra métricas por cada consulta en:

```text
data/metrics.jsonl
```

La interfaz Streamlit incluye una pestaña de observabilidad con los 8 KPIs solicitados.

### KPIs implementados

| # | KPI                         | Métrica                  | Umbral               |
| - | --------------------------- | ------------------------ | -------------------- |
| 1 | Tasa de éxito de tools      | `tool_success_rate`      | >= 95%               |
| 2 | Score del agente juez       | `judge_score`            | >= 7.5 / 10          |
| 3 | Time to Last Token          | `ttl_seconds`            | < 10 segundos        |
| 4 | Costo estimado por consulta | `estimated_cost_usd`     | < USD 0.05           |
| 5 | Tasa de error en cálculos   | `calculation_error_rate` | < 3%                 |
| 6 | Latencia RAG                | `rag_latency_seconds`    | < 2 segundos         |
| 7 | Cobertura del corpus RAG    | `rag_corpus_coverage`    | >= 85%               |
| 8 | Tokens promedio por sesión  | `avg_tokens_per_session` | Reportar y optimizar |

---

## 7. Corpus RAG

El corpus documental se encuentra en:

```text
data/documents/
```

Para el MVP se usan documentos de referencia sobre:

* Política de indicadores.
* Metodología de KPIs.
* Interpretación de siniestralidad.
* Lineamientos de reportes ejecutivos.

Ejemplo de documentos:

```text
01_politica_indicadores.txt
02_metodologia_kpis.txt
03_guia_interpretacion_siniestralidad.txt
04_lineamientos_reporte_ejecutivo.txt
```

---

## 8. Variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
APP_ENV=local
AWS_REGION=us-east-1
USE_BEDROCK=false

BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0

DOCUMENTS_PATH=./data/documents
PARQUET_PATH=./data/parquet
METRICS_PATH=./data/metrics.jsonl
REPORTS_PATH=./data/reports
```

---

## 9. Instalación local

### 9.1 Crear entorno virtual

En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 9.2 Actualizar pip

```powershell
python -m pip install --upgrade pip
```

### 9.3 Instalar dependencias

```powershell
pip install -r requirements.txt
```

---

## 10. Crear datos de prueba

Ejecutar:

```powershell
python scripts_create_sample_data.py
```

Este script genera:

```text
data/parquet/indicadores.parquet
```

También se puede crear el corpus documental con:

```powershell
python scripts_create_rag_documents.py
```

---

## 11. Ejecución del backend

Ejecutar FastAPI:

```powershell
python -m uvicorn app.main:app --reload
```

Endpoint local:

```text
http://127.0.0.1:8000
```

Documentación Swagger:

```text
http://127.0.0.1:8000/docs
```

Endpoint principal:

```text
POST /chat
```

Ejemplo de body:

```json
{
  "question": "Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF"
}
```

---

## 12. Ejecución del frontend

En una segunda terminal:

```powershell
.venv\Scripts\activate
streamlit run app/ui_streamlit.py
```

URL local:

```text
http://localhost:8501
```

---

## 13. Ejemplos de preguntas

```text
Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF
```

```text
¿Qué significa una siniestralidad alta y cómo debería interpretarse?
```

```text
¿Cuándo una brecha entre regionales debería considerarse una alerta?
```

```text
¿Qué métricas de observabilidad usa este sistema?
```

---

## 14. Respuesta esperada del sistema

Una consulta completa puede activar:

```text
rag_search
duckdb_analytics
kpi_calculator
pdf_report_generator
judge_llm
metrics_logger
```

Salida esperada:

* Respuesta textual.
* Fuentes recuperadas por RAG.
* SQL ejecutado.
* Resultados analíticos.
* Cálculo KPI.
* Ruta del PDF generado.
* Evaluación del agente juez.
* Métricas de observabilidad.

---

## 15. Preparación para AWS

La nube asignada para el proyecto es Amazon Web Services.

### Arquitectura AWS propuesta

| Necesidad                 | Servicio AWS                            |
| ------------------------- | --------------------------------------- |
| LLM principal             | Amazon Bedrock                          |
| Embeddings                | Amazon Titan Embeddings v2              |
| Almacenamiento documental | Amazon S3                               |
| Datos estructurados       | Amazon S3 + Parquet                     |
| Vector store              | OpenSearch Serverless o pgvector en RDS |
| Backend                   | ECS Fargate o EC2 con Docker            |
| API                       | API Gateway o ALB                       |
| Logs y métricas           | Amazon CloudWatch                       |
| Secretos                  | AWS Secrets Manager                     |
| CI/CD                     | GitHub Actions                          |

---

## 16. Selección del modelo LLM

### Modelo principal propuesto: Claude 3 Haiku

Se propone Claude 3 Haiku como modelo principal por:

* Baja latencia.
* Costo reducido.
* Buena capacidad de seguir instrucciones.
* Adecuado para respuestas analíticas estructuradas.
* Buena integración con Amazon Bedrock.

### Modelo fallback propuesto: Claude 3 Sonnet

Se propone Claude 3 Sonnet como fallback para:

* Consultas analíticas más complejas.
* Mayor razonamiento contextual.
* Evaluación avanzada del agente juez.
* Casos donde se requiera mayor calidad en síntesis ejecutiva.

### Parámetros sugeridos

```text
temperature = 0.2
top_p = 0.9
max_tokens = 900
```

Justificación:

* Temperatura baja para reducir variabilidad.
* Respuestas más determinísticas.
* Mayor control en dominios analíticos.
* Menor riesgo de alucinación.

---

## 17. Limitaciones del MVP

Este prototipo se ejecuta localmente y prioriza demostrar el flujo funcional completo.

Limitaciones actuales:

* El RAG local usa TF-IDF, no embeddings productivos.
* El vector store es local, no OpenSearch ni pgvector.
* El costo Bedrock es estimado.
* El agente juez usa fallback heurístico cuando `USE_BEDROCK=false`.
* Los datos Parquet son datos de prueba.
* CloudWatch está planteado como arquitectura objetivo, no como integración obligatoria local.
* La autenticación de usuarios no está implementada.
* La seguridad IAM se documenta para la versión AWS.

---

## 18. Cómo validar el MVP

1. Levantar FastAPI.
2. Levantar Streamlit.
3. Ejecutar una consulta con regional, promedio y PDF.
4. Verificar que se activen las tools.
5. Confirmar que se genere un PDF.
6. Revisar la evaluación del agente juez.
7. Revisar las 8 tarjetas KPI en la pestaña de métricas.
8. Confirmar que se escriba el archivo `data/metrics.jsonl`.

---

## 19. Estado actual

Estado del MVP:

```text
Backend FastAPI: funcional
Frontend Streamlit: funcional
RAG local: funcional
DuckDB sobre Parquet: funcional
KPI Calculator: funcional
PDF Generator: funcional
Judge Agent: funcional
Métricas locales: funcional
Preparación Bedrock: implementada con fallback
Dashboard 8 KPIs: funcional
```

---


