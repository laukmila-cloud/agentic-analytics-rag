# Agentic Analytics RAG

Sistema agéntico analítico desarrollado en Python para responder preguntas de negocio usando **LLM + RAG + Tools + Agente Juez**, con interfaz en Streamlit, backend en FastAPI, observabilidad local y arquitectura preparada para AWS.

Este proyecto fue construido como una prueba técnica para demostrar un flujo completo de análisis asistido por IA: recuperación documental, consulta de datos estructurados, cálculo de KPIs, generación de reportes PDF y evaluación automática de calidad de la respuesta.

---

## Enlaces de entrega

- **Repositorio público:** https://github.com/laukmila-cloud/agentic-analytics-rag
- **Video demo:** Pendiente de agregar
- **Nube asignada:** Amazon Web Services
- **Lenguaje principal:** Python 3.12+
- **Backend:** FastAPI
- **Interfaz:** Streamlit
- **Base analítica local:** DuckDB + Parquet
- **RAG local:** Índice persistente con recuperación vectorial y reranking híbrido

---

## Estado de la entrega

Este proyecto corresponde a un **MVP local funcional con arquitectura preparada para AWS**.

El sistema implementa:

- Orquestador agéntico.
- Patrón **Orchestrator & Sub-workers**.
- Recuperación documental con RAG local persistente.
- Ingesta documental, chunking, recuperación y reranking híbrido.
- Herramientas externas para análisis de datos, cálculo KPI y generación de reportes PDF.
- Agente juez con fallback local y preparación para Amazon Bedrock.
- Control de calidad mediante umbral `judge_score >= 7.5`.
- Dashboard de observabilidad con 8 KPIs.
- Documentación técnica en español.
- Dockerfile para contenerización.
- GitHub Actions para validación automática con pruebas y Ruff.

La integración con Amazon Bedrock está preparada mediante la variable:

```env
USE_BEDROCK=true
```

Por defecto, la demo local usa:

```env
USE_BEDROCK=false
```

Esto permite ejecutar el proyecto sin credenciales AWS. El despliegue en AWS, CloudWatch y vector store administrado se documentan como arquitectura objetivo.

---

## Nota sobre el corpus documental

Por confidencialidad, el corpus incluido corresponde a **documentos sintéticos representativos del dominio**.

Estos documentos simulan políticas, metodologías e interpretación de indicadores para demostrar el flujo RAG sin exponer información sensible, privada o propietaria.

El corpus se encuentra en:

```text
data/documents/
```

La solución está diseñada para reemplazar este corpus sintético por documentos reales en un entorno productivo, manteniendo el mismo flujo de ingesta, chunking, recuperación, reranking y evaluación.

---

## Objetivo del sistema

El sistema permite que un usuario realice preguntas de negocio como:

```text
Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF.
```

A partir de esa consulta, el sistema:

1. Recupera contexto documental relevante mediante RAG.
2. Ejecuta análisis estructurado sobre datos Parquet usando DuckDB.
3. Calcula KPIs complementarios.
4. Genera una respuesta ejecutiva.
5. Evalúa la respuesta con un agente juez.
6. Registra métricas de observabilidad.
7. Genera un reporte PDF descargable si el usuario lo solicita.

---

## Arquitectura general

La solución sigue un patrón agéntico modular:

```text
Usuario
  |
  v
Streamlit UI
  |
  v
FastAPI Backend
  |
  v
Agent Orchestrator
  |
  |-- RAG Worker
  |     |-- Local Vector Store
  |     |-- Document Chunking
  |     |-- Hybrid Reranking
  |
  |-- Analytics Worker
  |     |-- DuckDB Tool
  |     |-- Parquet Data
  |
  |-- KPI Calculator Tool
  |
  |-- Report Worker
  |     |-- PDF Generator
  |
  |-- Judge Agent
  |     |-- Heuristic Judge
  |     |-- Bedrock-ready Judge LLM
  |
  |-- Metrics Logger
        |-- metrics.jsonl
        |-- Streamlit Dashboard
```

---

## Componentes principales

### 1. Orquestador agéntico

Archivo principal:

```text
orchestrator/agent_orchestrator.py
```

Responsabilidades:

- Coordinar el flujo completo de la consulta.
- Ejecutar recuperación documental.
- Decidir si se requiere análisis estructurado.
- Ejecutar herramientas externas.
- Componer la respuesta final.
- Invocar el agente juez.
- Generar reportes PDF.
- Registrar métricas de observabilidad.

---

### 2. RAG local persistente

Archivos principales:

```text
rag/vector_store.py
rag/local_retriever.py
workers/rag_worker.py
```

Funciones implementadas:

- Lectura de documentos `.txt` y `.pdf`.
- Chunking con solapamiento.
- Índice persistente local.
- Recuperación por similitud.
- Reranking híbrido combinando señales vectoriales y palabras clave.
- Métricas de recuperación como latencia, chunks encontrados y cobertura.

La cobertura RAG se calcula usando `raw_score` o `rerank_score`, evitando depender del score normalizado final.

---

### 3. Herramientas externas

El sistema implementa herramientas tipo MCP/tools a nivel local:

```text
tools/duckdb_tool.py
tools/kpi_calculator.py
tools/pdf_generator.py
```

#### DuckDB Tool

Ejecuta consultas analíticas sobre datos Parquet.

Ejemplo de salida:

```text
Promedio del indicador por regional.
Total de registros.
Agrupaciones por mes o regional.
```

#### KPI Calculator

Calcula diferencias entre indicadores, brechas y valores comparativos.

Ejemplo:

```text
Diferencia absoluta entre Bogotá y Antioquia.
Regional con mayor promedio.
```

#### PDF Generator

Genera reportes PDF a partir de la respuesta ejecutiva final.

Los reportes se guardan localmente en:

```text
data/reports/
```

Esta carpeta está excluida del repositorio mediante `.gitignore`.

---

### 4. Agente juez

Archivo principal:

```text
judge/judge_llm.py
```

El agente juez evalúa:

- Relevancia frente a la pregunta.
- Uso correcto del contexto RAG.
- Precisión numérica.
- Riesgo de alucinación.
- Claridad de la respuesta.
- Suficiencia del corpus documental.

El sistema usa un umbral operativo:

```text
judge_score >= 7.5
```

Si la respuesta no alcanza el umbral, el orquestador agrega una advertencia:

```text
Advertencia del agente juez
```

Esto demuestra que el juez no solo califica, sino que también participa en el control de calidad del flujo.

---

### 5. Integración LLM / Bedrock-ready

Archivo principal:

```text
llm/bedrock_client.py
```

El sistema está preparado para usar Amazon Bedrock.

Por defecto:

```env
USE_BEDROCK=false
```

En modo local, el sistema usa respuestas fallback determinísticas para permitir la ejecución sin credenciales cloud.

Para activar Bedrock:

```env
USE_BEDROCK=true
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
```

---

## Observabilidad

El sistema registra métricas en:

```text
data/metrics.jsonl
```

También muestra un dashboard en Streamlit.

### KPIs implementados

| KPI | Descripción |
|---|---|
| `tool_success_rate` | Porcentaje de herramientas ejecutadas correctamente |
| `judge_score` | Puntaje entregado por el agente juez |
| `judge_passed` | Indica si la respuesta superó el umbral del juez |
| `ttl_seconds` | Tiempo total de respuesta |
| `estimated_cost_usd` | Estimación local de costo por consulta |
| `calculation_error_rate` | Tasa de error en cálculos analíticos |
| `rag_latency_seconds` | Latencia del componente RAG |
| `rag_corpus_coverage` | Indica si el corpus recuperado soporta la consulta |
| `avg_tokens_per_session` | Estimación de tokens por sesión |

### Umbrales de referencia

| Métrica | Umbral |
|---|---:|
| `tool_success_rate` | >= 0.95 |
| `judge_score` | >= 7.5 |
| `ttl_seconds` | < 10 segundos |
| `estimated_cost_usd` | < 0.05 USD |
| `calculation_error_rate` | < 0.03 |
| `rag_latency_seconds` | < 2 segundos |
| `rag_corpus_coverage` | >= 0.85 |
| `avg_tokens_per_session` | Reportado y monitoreado |

---

## Interfaz de usuario

La interfaz está desarrollada en Streamlit.

Archivo principal:

```text
app/ui_streamlit.py
```

Permite:

- Escribir consultas de negocio.
- Ejecutar análisis.
- Ver respuesta ejecutiva.
- Descargar reporte PDF.
- Consultar fuentes recuperadas.
- Ver soporte técnico.
- Revisar métricas de observabilidad.
- Consultar arquitectura general.

---

## Backend API

El backend está desarrollado con FastAPI.

Archivo principal:

```text
app/main.py
```

### Endpoint de salud

```http
GET /
```

Respuesta esperada:

```json
{
  "status": "ok",
  "message": "Sistema agéntico activo"
}
```

### Endpoint de chat

```http
POST /chat
```

Ejemplo de payload:

```json
{
  "question": "Compara el promedio del indicador de siniestralidad por regional"
}
```

---

## Estructura del proyecto

```text
agentic-analytics-rag/
│
├── app/
│   ├── config.py
│   ├── main.py
│   ├── schemas.py
│   └── ui_streamlit.py
│
├── orchestrator/
│   └── agent_orchestrator.py
│
├── workers/
│   ├── analytics_worker.py
│   ├── rag_worker.py
│   └── report_worker.py
│
├── rag/
│   ├── local_retriever.py
│   └── vector_store.py
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
│   └── parquet/
│
├── docs/
│   ├── arquitectura.md
│   ├── administrador.md
│   └── guia_usuario.md
│
├── tests/
│   └── test_smoke.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example
├── requirements.txt
└── README.md
```

---

## Requisitos

- Python 3.12+
- pip
- Git
- PowerShell o terminal compatible
- Opcional: Docker
- Opcional: credenciales AWS para activar Bedrock

---

## Instalación local

Clonar el repositorio:

```powershell
git clone https://github.com/laukmila-cloud/agentic-analytics-rag.git
cd agentic-analytics-rag
```

Crear entorno virtual:

```powershell
python -m venv .venv
```

Activar entorno virtual en Windows:

```powershell
.venv\Scripts\activate
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Crear archivo `.env` desde el ejemplo:

```powershell
Copy-Item .env.example .env
```

---

## Variables de entorno

Ejemplo:

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
VECTOR_STORE_PATH=./data/vector_store
```

---

## Ejecución local

### 1. Ejecutar backend FastAPI

```powershell
python -m uvicorn app.main:app --reload
```

El backend quedará disponible en:

```text
http://127.0.0.1:8000
```

Documentación automática:

```text
http://127.0.0.1:8000/docs
```

---

### 2. Ejecutar interfaz Streamlit

En otra terminal:

```powershell
streamlit run app/ui_streamlit.py
```

La interfaz quedará disponible en:

```text
http://localhost:8501
```

---

## Consultas de prueba

Consulta analítica con RAG y tools:

```text
Compara el promedio del indicador de siniestralidad por regional
```

Consulta con reporte PDF:

```text
Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF
```

Consulta fuera del dominio para probar el agente juez:

```text
Dame una receta de pasta con tomate
```

En esta última consulta, el juez debería reducir el puntaje, marcar riesgo de alucinación alto o medio y mostrar una advertencia si el puntaje queda por debajo del umbral.

---

## Pruebas

Ejecutar pruebas unitarias básicas:

```powershell
pytest
```

Resultado esperado:

```text
3 passed
```

Ejecutar validación crítica con Ruff:

```powershell
ruff check . --select E9,F63,F7,F82
```

---

## CI/CD

El proyecto incluye GitHub Actions en:

```text
.github/workflows/ci.yml
```

El workflow ejecuta:

1. Checkout del repositorio.
2. Configuración de Python 3.12.
3. Instalación de dependencias.
4. Validación crítica con Ruff.
5. Ejecución de pruebas con Pytest.

---

## Docker

El proyecto incluye un Dockerfile para contenerización.

Construir imagen:

```powershell
docker build -t agentic-analytics-rag .
```

Ejecutar contenedor:

```powershell
docker run -p 8000:8000 -p 8501:8501 agentic-analytics-rag
```

Servicios expuestos:

```text
FastAPI: http://localhost:8000
Streamlit: http://localhost:8501
```

---

## Arquitectura objetivo en AWS

La arquitectura propuesta para despliegue real contempla:

| Componente local | Servicio AWS objetivo |
|---|---|
| Streamlit | ECS Fargate, EC2 o App Runner |
| FastAPI | ECS Fargate, Lambda + API Gateway o App Runner |
| Documentos locales | Amazon S3 |
| Datos Parquet locales | Amazon S3 |
| Vector store local | Amazon OpenSearch Serverless o RDS PostgreSQL con pgvector |
| LLM local/fallback | Amazon Bedrock |
| Embeddings locales/fallback | Amazon Bedrock Titan Embeddings |
| Métricas locales JSONL | Amazon CloudWatch |
| Reportes PDF locales | Amazon S3 |
| CI/CD local GitHub Actions | GitHub Actions + despliegue AWS |

---

## Ruta de despliegue real en AWS

Para llevar este MVP a un entorno cloud funcional:

1. Crear bucket S3 para documentos, datos Parquet y reportes.
2. Crear índice vectorial en Amazon OpenSearch Serverless o RDS PostgreSQL con pgvector.
3. Activar Amazon Bedrock en la región seleccionada.
4. Configurar permisos IAM para Bedrock, S3, CloudWatch y servicio de cómputo.
5. Contenerizar la aplicación con Docker.
6. Desplegar backend e interfaz en ECS Fargate, EC2 o App Runner.
7. Redirigir logs y métricas a CloudWatch.
8. Configurar alarmas para latencia, errores de tools, score del juez y cobertura RAG.
9. Automatizar despliegue con GitHub Actions.

---

## Limitaciones actuales

- El sistema se entrega como MVP local funcional.
- No incluye evidencia de despliegue productivo real en AWS.
- Amazon Bedrock está preparado por configuración, pero no activado por defecto.
- CloudWatch está documentado como arquitectura objetivo; la observabilidad local se registra en JSONL y dashboard Streamlit.
- El corpus documental incluido es sintético por confidencialidad.
- Las pruebas automatizadas son básicas y pueden ampliarse para cubrir más rutas del orquestador.
- La estimación de costo es local y aproximada; en Bedrock real debe calcularse con tokens reales de entrada y salida.

---

## Cumplimiento de la prueba técnica

| Requisito | Estado |
|---|---|
| Sistema agéntico con orquestador | Implementado |
| Patrón Orchestrator & Sub-workers | Implementado |
| RAG con ingesta, chunking, recuperación y reranking | Implementado en MVP local |
| Vector store | Implementado localmente con índice persistente |
| Tools externas mínimas | Implementadas: DuckDB, KPI Calculator, PDF Generator |
| Agente juez | Implementado con fallback local y preparado para Bedrock |
| Juez con umbral operativo | Implementado |
| Observabilidad con 8 KPIs | Implementada |
| Dashboard | Implementado en Streamlit |
| Generación de PDF | Implementada |
| Documentación en español | Implementada |
| Dockerfile | Incluido |
| GitHub Actions | Incluido |
| Validación con Ruff | Incluida |
| AWS Bedrock | Preparado por configuración |
| Despliegue AWS real | Documentado como ruta objetivo |
| Video demo | Pendiente de agregar enlace |

---

## Documentación adicional

La documentación completa se encuentra en:

```text
docs/
```

Archivos principales:

```text
docs/arquitectura.md
docs/administrador.md
docs/guia_usuario.md
```

---

## Autoría

Proyecto desarrollado como prueba técnica para demostrar capacidades en:

- Python.
- FastAPI.
- Streamlit.
- RAG.
- Sistemas agénticos.
- Tools externas.
- Evaluación con agente juez.
- Observabilidad.
- Arquitectura cloud-ready para AWS.


