# Documento de Administrador

## Sistema Agéntico Analítico con LLM + RAG + Tools

**Proyecto:** Sistema Agéntico Analítico con LLM + RAG + Tools
**Lenguaje:** Python 3.12+
**Backend:** FastAPI
**Frontend:** Streamlit
**Nube objetivo:** Amazon Web Services
**Modo local:** Disponible con `USE_BEDROCK=false`
**Modo AWS:** Disponible con `USE_BEDROCK=true` y credenciales configuradas

---

## 1. Propósito del documento

Este documento describe las instrucciones técnicas necesarias para instalar, configurar, ejecutar, administrar y desplegar el sistema agéntico analítico.

Está dirigido a un administrador técnico, DevOps, cloud engineer o desarrollador responsable de operar la aplicación en ambiente local o en AWS.

---

## 2. Descripción operativa del sistema

El sistema permite realizar consultas analíticas en lenguaje natural sobre indicadores de desempeño.

Componentes principales:

* Frontend en Streamlit.
* Backend en FastAPI.
* Agente orquestador.
* Worker RAG.
* Tool DuckDB sobre Parquet.
* Tool calculadora de KPIs.
* Tool generadora de PDF.
* Agente juez.
* Registro de métricas locales.
* Integración preparada con Amazon Bedrock.

---

## 3. Prerrequisitos locales

Para ejecutar el sistema localmente se requiere:

| Recurso           | Versión / requisito                             |
| ----------------- | ----------------------------------------------- |
| Sistema operativo | Windows, Linux o macOS                          |
| Python            | 3.12 o superior                                 |
| pip               | Última versión disponible                       |
| Git               | Recomendado                                     |
| VS Code           | Recomendado                                     |
| Navegador         | Chrome, Edge, Firefox o similar                 |
| Memoria RAM       | 4 GB mínimo, 8 GB recomendado                   |
| Espacio en disco  | 1 GB mínimo para dependencias, datos y reportes |

---

## 4. Prerrequisitos AWS

Para ejecutar el sistema con servicios AWS se requiere:

* Cuenta activa de AWS.
* Usuario o rol IAM con permisos mínimos necesarios.
* Acceso habilitado a Amazon Bedrock.
* Modelo Bedrock habilitado en la región seleccionada.
* Bucket S3 para corpus, datos y reportes.
* Servicio de cómputo: ECS Fargate o EC2.
* CloudWatch habilitado para logs y métricas.
* Secrets Manager para variables sensibles.
* Opcional: OpenSearch Serverless o RDS con pgvector para vector store productivo.

---

## 5. Permisos IAM recomendados

Para un ambiente MVP se recomiendan permisos controlados sobre los siguientes servicios:

```text
bedrock:InvokeModel
bedrock:InvokeModelWithResponseStream
s3:GetObject
s3:PutObject
s3:ListBucket
logs:CreateLogGroup
logs:CreateLogStream
logs:PutLogEvents
cloudwatch:PutMetricData
secretsmanager:GetSecretValue
```

Si se usa OpenSearch Serverless:

```text
aoss:APIAccessAll
aoss:BatchGetCollection
aoss:CreateCollection
aoss:ListCollections
```

Si se usa RDS con pgvector:

```text
rds-db:connect
secretsmanager:GetSecretValue
```

En producción se debe aplicar principio de mínimo privilegio, separando roles para aplicación, despliegue, observabilidad y administración.

---

## 6. Estructura esperada del proyecto

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
│   ├── reports/
│   └── metrics.jsonl
│
├── docs/
│   ├── arquitectura.md
│   ├── administrador.md
│   └── guia_usuario.md
│
├── requirements.txt
├── README.md
└── .env
```

---

## 7. Instalación local

### 7.1 Clonar el repositorio

```powershell
git clone <URL_DEL_REPOSITORIO>
cd agentic-analytics-rag
```

Si se trabaja desde una carpeta local ya creada, ingresar directamente:

```powershell
cd agentic-analytics-rag
```

---

### 7.2 Crear entorno virtual

En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

En Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 7.3 Actualizar pip

```powershell
python -m pip install --upgrade pip
```

---

### 7.4 Instalar dependencias

```powershell
pip install -r requirements.txt
```

---

## 8. Archivo de variables de entorno

Crear un archivo `.env` en la raíz del proyecto.

Contenido recomendado para ejecución local:

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

## 9. Configuración de Bedrock

Para usar Amazon Bedrock se debe cambiar:

```env
USE_BEDROCK=true
```

Además, se deben configurar credenciales AWS.

En ambiente local se puede usar:

```powershell
aws configure
```

Variables requeridas:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
```

En AWS se recomienda usar IAM Role asociado al servicio de cómputo, no credenciales estáticas.

---

## 10. Creación de datos de prueba

El sistema requiere un archivo Parquet de indicadores.

Ejecutar:

```powershell
python scripts_create_sample_data.py
```

Esto crea:

```text
data/parquet/indicadores.parquet
```

---

## 11. Creación del corpus RAG

El sistema requiere documentos en:

```text
data/documents/
```

Para crear documentos de prueba:

```powershell
python scripts_create_rag_documents.py
```

Documentos esperados:

```text
01_politica_indicadores.txt
02_metodologia_kpis.txt
03_guia_interpretacion_siniestralidad.txt
04_lineamientos_reporte_ejecutivo.txt
```

---

## 12. Ejecución del backend

Ejecutar FastAPI:

```powershell
python -m uvicorn app.main:app --reload
```

URLs disponibles:

```text
Health check:
http://127.0.0.1:8000

Documentación Swagger:
http://127.0.0.1:8000/docs

Endpoint principal:
POST http://127.0.0.1:8000/chat
```

Ejemplo de request:

```json
{
  "question": "Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF"
}
```

---

## 13. Ejecución del frontend

Abrir una segunda terminal, activar el entorno virtual y ejecutar:

```powershell
streamlit run app/ui_streamlit.py
```

URL local:

```text
http://localhost:8501
```

---

## 14. Procedimiento de ingesta de nuevos documentos

Para agregar documentos al corpus RAG:

1. Validar que el documento sea pertinente para el dominio.
2. Guardar el archivo en:

```text
data/documents/
```

3. Usar formato `.txt` o `.pdf`.
4. Reiniciar backend si se requiere limpiar estado de ejecución.
5. Ejecutar una consulta desde Streamlit.
6. Validar que el documento aparezca en fuentes RAG.

Formatos soportados en el MVP:

```text
.txt
.pdf
```

Codificación recomendada para TXT:

```text
UTF-8
```

---

## 15. Procedimiento para actualizar datos Parquet

Para actualizar los indicadores estructurados:

1. Crear o reemplazar el archivo:

```text
data/parquet/indicadores.parquet
```

2. Mantener el esquema mínimo esperado:

```text
mes
regional
indicador
valor_indicador
```

3. Verificar que `valor_indicador` sea numérico.
4. Reiniciar backend si la consulta queda en caché.
5. Ejecutar consulta de validación:

```text
Compara el promedio del indicador de siniestralidad por regional
```

---

## 16. Reportes PDF

Los reportes generados se guardan en:

```text
data/reports/
```

Se activa la generación PDF cuando la pregunta contiene palabras como:

```text
reporte
pdf
informe
descargar
documento
```

Ejemplo:

```text
Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF
```

---

## 17. Métricas y observabilidad local

Cada consulta genera una fila JSON en:

```text
data/metrics.jsonl
```

El dashboard Streamlit muestra:

1. Tasa de éxito de tools.
2. Score del agente juez.
3. Time to Last Token.
4. Costo estimado por consulta.
5. Tasa de error en cálculos.
6. Latencia del pipeline RAG.
7. Cobertura del corpus RAG.
8. Tokens promedio por sesión.

---

## 18. Configuración de CloudWatch propuesta

En AWS, las métricas locales deben migrarse a CloudWatch.

Flujo recomendado:

```text
Aplicación
→ Logs JSON estructurados
→ CloudWatch Logs
→ CloudWatch Metrics
→ CloudWatch Dashboard
→ Alarmas
```

Métricas a publicar:

```text
tool_success_rate
judge_score
ttl_seconds
estimated_cost_usd
calculation_error_rate
rag_latency_seconds
rag_corpus_coverage
avg_tokens_per_session
```

---

## 19. Alertas recomendadas en CloudWatch

| Métrica                  | Condición de alerta |
| ------------------------ | ------------------- |
| `tool_success_rate`      | Menor a 0.95        |
| `judge_score`            | Menor a 7.5         |
| `ttl_seconds`            | Mayor a 10          |
| `estimated_cost_usd`     | Mayor a 0.05        |
| `calculation_error_rate` | Mayor a 0.03        |
| `rag_latency_seconds`    | Mayor a 2           |
| `rag_corpus_coverage`    | Menor a 0.85        |

---

## 20. Despliegue local con Docker

El proyecto puede empaquetarse en Docker.

Comando sugerido de construcción:

```powershell
docker build -t agentic-analytics-rag .
```

Comando sugerido de ejecución:

```powershell
docker run -p 8000:8000 -p 8501:8501 agentic-analytics-rag
```

En el MVP, si backend y frontend se empaquetan separados, se recomienda usar dos contenedores:

```text
Contenedor 1: FastAPI
Contenedor 2: Streamlit
```

---

## 21. Despliegue recomendado en AWS

### Opción recomendada: ECS Fargate

Servicios:

```text
ECS Fargate
Application Load Balancer
Amazon S3
Amazon Bedrock
CloudWatch
Secrets Manager
OpenSearch Serverless o RDS pgvector
```

Flujo:

```text
Usuario
→ Load Balancer
→ ECS Service Frontend Streamlit
→ ECS Service Backend FastAPI
→ Bedrock / S3 / Vector Store / CloudWatch
```

---

### Opción alternativa: EC2 con Docker

Para una demo rápida:

1. Crear instancia EC2.
2. Instalar Docker.
3. Clonar repositorio.
4. Crear `.env`.
5. Ejecutar contenedores.
6. Abrir puertos necesarios.
7. Configurar seguridad con Security Groups.

Puertos:

```text
8000 FastAPI
8501 Streamlit
```

---

## 22. Secrets Manager

En AWS, las variables sensibles o de configuración deben almacenarse en Secrets Manager.

Ejemplo de secreto:

```json
{
  "APP_ENV": "production",
  "AWS_REGION": "us-east-1",
  "USE_BEDROCK": "true",
  "BEDROCK_MODEL_ID": "anthropic.claude-3-haiku-20240307-v1:0",
  "DOCUMENTS_BUCKET": "agentic-rag-documents",
  "REPORTS_BUCKET": "agentic-rag-reports"
}
```

---

## 23. Procedimiento de rollback

En caso de falla en despliegue:

1. Identificar la versión anterior estable del contenedor o commit.
2. Revisar logs en CloudWatch.
3. Detener el servicio actual o revertir task definition.
4. Restaurar variables de entorno anteriores.
5. Desplegar la imagen anterior.
6. Ejecutar pruebas de humo.
7. Validar `/chat`.
8. Validar Streamlit.
9. Validar generación de métricas.

Prueba mínima de rollback:

```text
GET /
POST /chat
Consulta con DuckDB
Consulta con RAG
Consulta con PDF
```

---

## 24. Manejo de errores

### 24.1 Error de backend no disponible

Síntoma:

```text
No fue posible consultar el backend
```

Acciones:

1. Verificar que FastAPI esté corriendo.
2. Verificar URL `http://127.0.0.1:8000`.
3. Revisar puerto 8000.
4. Reiniciar backend.

---

### 24.2 Error por archivo Parquet inexistente

Síntoma:

```text
No existe el archivo data/parquet/indicadores.parquet
```

Acción:

```powershell
python scripts_create_sample_data.py
```

---

### 24.3 Error por documentos RAG inexistentes

Síntoma:

```text
No hay documentos cargados en data/documents
```

Acción:

```powershell
python scripts_create_rag_documents.py
```

---

### 24.4 Error de Bedrock

Posibles causas:

* `USE_BEDROCK=true` sin credenciales configuradas.
* Modelo no habilitado en la región.
* Permisos IAM insuficientes.
* Región incorrecta.
* Límite de cuota.

Acciones:

1. Cambiar temporalmente a:

```env
USE_BEDROCK=false
```

2. Verificar credenciales AWS.
3. Confirmar acceso al modelo en Amazon Bedrock.
4. Revisar CloudWatch.
5. Validar permisos IAM.

---

### 24.5 Error en generación PDF

Posibles causas:

* Carpeta `data/reports` sin permisos.
* Dependencia ReportLab no instalada.
* Contenido demasiado largo sin manejo de páginas.

Acciones:

1. Verificar instalación:

```powershell
pip install reportlab
```

2. Crear carpeta:

```powershell
mkdir data\reports
```

3. Reintentar consulta con “genera un reporte PDF”.

---

## 25. Pruebas de humo

Después de cualquier instalación o despliegue, ejecutar estas pruebas:

### 25.1 Health check

```text
GET http://127.0.0.1:8000/
```

Resultado esperado:

```json
{
  "status": "ok",
  "message": "Sistema agéntico activo"
}
```

---

### 25.2 Consulta RAG

```text
¿Qué significa una siniestralidad alta?
```

Resultado esperado:

* Recupera fuente documental.
* Respuesta con contexto.
* Score del juez.

---

### 25.3 Consulta analítica

```text
Compara el promedio del indicador de siniestralidad por regional
```

Resultado esperado:

* Ejecuta DuckDB.
* Retorna datos por regional.
* Calcula KPI.

---

### 25.4 Consulta con PDF

```text
Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF
```

Resultado esperado:

* Ejecuta RAG.
* Ejecuta DuckDB.
* Ejecuta KPI Calculator.
* Ejecuta PDF Generator.
* Genera archivo en `data/reports`.

---

## 26. Mantenimiento recomendado

Tareas periódicas:

* Revisar tamaño de `data/metrics.jsonl`.
* Limpiar reportes antiguos en `data/reports`.
* Actualizar corpus documental.
* Validar calidad de chunks RAG.
* Revisar costos Bedrock.
* Revisar métricas de latencia.
* Validar tasa de éxito de tools.
* Ejecutar pruebas antes de despliegues.

---

## 27. Checklist de operación

Antes de una demo o entrega:

```text
[ ] Entorno virtual activo
[ ] Dependencias instaladas
[ ] Archivo .env creado
[ ] Backend FastAPI funcionando
[ ] Frontend Streamlit funcionando
[ ] Parquet generado
[ ] Corpus RAG disponible
[ ] Consulta RAG validada
[ ] Consulta DuckDB validada
[ ] KPI Calculator validado
[ ] PDF Generator validado
[ ] Agente juez funcionando
[ ] Dashboard de 8 KPIs visible
[ ] README actualizado
[ ] Documentos en /docs completos
[ ] Repositorio GitHub actualizado
```

---

## 28. Conclusión

El sistema está preparado para ejecutarse localmente como MVP funcional y para evolucionar hacia un despliegue cloud en AWS. La administración del sistema requiere mantener actualizados el corpus documental, los datos Parquet, las variables de entorno, las métricas de observabilidad y los permisos asociados a servicios AWS.

La operación recomendada consiste en validar primero el flujo local completo y luego migrar progresivamente almacenamiento, modelos, vector store y observabilidad hacia servicios administrados de AWS.
