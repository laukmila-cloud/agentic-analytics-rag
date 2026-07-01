# Guía de Usuario

## Sistema Agéntico Analítico con LLM + RAG + Tools

**Proyecto:** Sistema Agéntico Analítico con LLM + RAG + Tools
**Dominio:** Indicadores financieros y de desempeño
**Interfaz:** Streamlit
**Usuario objetivo:** Usuario de negocio, analista, evaluador técnico o administrador funcional

---

## 1. Propósito de esta guía

Esta guía explica cómo usar el sistema agéntico analítico desde la interfaz web.

El documento está escrito en lenguaje funcional y no técnico para que cualquier usuario pueda entender:

* Qué hace el sistema.
* Cómo realizar una consulta.
* Qué tipos de preguntas puede responder.
* Cómo interpretar los resultados.
* Cómo descargar reportes PDF.
* Cómo leer las métricas del dashboard.
* Qué limitaciones tiene el sistema.

---

## 2. ¿Qué es este sistema?

El sistema es un asistente analítico que permite hacer preguntas en lenguaje natural sobre indicadores de desempeño.

En lugar de escribir consultas SQL o revisar documentos manualmente, el usuario puede escribir preguntas como:

```text id="uypwbv"
Compara el promedio del indicador de siniestralidad por regional
```

o:

```text id="dqa7lg"
¿Qué significa una siniestralidad alta y cómo debería interpretarse?
```

El sistema procesa la pregunta, revisa documentos de referencia, consulta datos estructurados, calcula KPIs cuando aplica, genera una respuesta y valida la calidad de esa respuesta mediante un agente juez.

---

## 3. ¿Para qué sirve?

El sistema sirve para:

* Consultar indicadores de negocio.
* Comparar resultados por regional.
* Interpretar siniestralidad.
* Revisar documentos de metodología o políticas internas.
* Calcular diferencias entre indicadores.
* Generar reportes PDF.
* Monitorear calidad, costo y desempeño de las respuestas.
* Apoyar análisis ejecutivo de datos.

---

## 4. Flujo general de uso

El flujo de uso es el siguiente:

```text id="v9notd"
1. Abrir la interfaz web.
2. Seleccionar o escribir una pregunta.
3. Presionar el botón "Ejecutar consulta".
4. Esperar la respuesta del sistema.
5. Revisar las herramientas ejecutadas.
6. Leer la respuesta generada.
7. Revisar las fuentes documentales usadas.
8. Consultar el resultado del agente juez.
9. Descargar el PDF si fue solicitado.
10. Revisar las métricas en el dashboard.
```

---

## 5. Acceso al sistema

Para abrir la interfaz local, el usuario debe ingresar en el navegador a:

```text id="wbr1z7"
http://localhost:8501
```

La interfaz tiene tres pestañas principales:

```text id="a8iwem"
Consulta
Métricas
Arquitectura
```

---

## 6. Pestaña Consulta

La pestaña **Consulta** es la sección principal del sistema.

Desde esta pestaña el usuario puede:

* Seleccionar una pregunta sugerida.
* Escribir una pregunta personalizada.
* Ejecutar el sistema agéntico.
* Leer la respuesta.
* Ver qué herramientas se usaron.
* Consultar fuentes recuperadas.
* Revisar la evaluación del agente juez.
* Descargar un reporte PDF cuando aplique.

---

## 7. Preguntas sugeridas

La interfaz incluye preguntas sugeridas para facilitar la demostración.

Ejemplos:

```text id="hfstqh"
Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF
```

```text id="v85951"
¿Qué significa una siniestralidad alta y cómo debería interpretarse?
```

```text id="d2rwzm"
¿Cuándo una brecha entre regionales debería considerarse una alerta?
```

```text id="esjoeu"
¿Qué métricas de observabilidad usa este sistema?
```

Estas preguntas permiten demostrar diferentes capacidades del sistema.

---

## 8. Cómo realizar una consulta paso a paso

### Paso 1: Abrir la interfaz

Ingresar a:

```text id="cxly1b"
http://localhost:8501
```

---

### Paso 2: Ir a la pestaña Consulta

Seleccionar la pestaña:

```text id="2lxqe1"
Consulta
```

---

### Paso 3: Seleccionar o escribir una pregunta

El usuario puede usar una pregunta sugerida o escribir una propia.

Ejemplo:

```text id="ygfnpf"
Compara el promedio del indicador de siniestralidad por regional
```

---

### Paso 4: Ejecutar la consulta

Presionar el botón:

```text id="1s24rj"
Ejecutar consulta
```

---

### Paso 5: Revisar la respuesta

El sistema mostrará una respuesta estructurada con:

* Contexto recuperado desde documentos.
* Resultado analítico.
* Interpretación ejecutiva.
* Cálculos KPI si aplican.
* Advertencias o limitaciones.

---

### Paso 6: Revisar herramientas ejecutadas

La interfaz muestra etiquetas con las herramientas usadas, por ejemplo:

```text id="afyg3s"
RAG · OK
DuckDB · OK
KPI Calculator · OK
PDF Generator · OK
```

Cuando una herramienta se ejecuta correctamente aparece en estado **OK**.

Si ocurre un error, aparecerá en estado **ERROR**.

---

### Paso 7: Revisar fuentes RAG

La sección **Fuentes RAG** muestra los documentos utilizados para construir la respuesta.

Ejemplo:

```text id="dl7i2j"
01_politica_indicadores.txt
02_metodologia_kpis.txt
03_guia_interpretacion_siniestralidad.txt
```

Esto permite saber de dónde salió el contexto usado por el sistema.

---

### Paso 8: Revisar el agente juez

El agente juez evalúa la respuesta antes de entregarla.

La interfaz muestra información como:

```json id="31qjjc"
{
  "score": 8.0,
  "verdict": "Respuesta aprobada por juez heurístico local.",
  "numeric_precision": "Sin errores numéricos detectados automáticamente.",
  "hallucination_risk": "Bajo",
  "improvement_suggestion": "Activar USE_BEDROCK=true para evaluación con Judge LLM en Amazon Bedrock."
}
```

---

## 9. Tipos de consultas soportadas

El sistema soporta diferentes tipos de consultas.

---

### 9.1 Consultas documentales

Estas consultas recuperan información desde documentos del corpus RAG.

Ejemplo:

```text id="y8q3th"
¿Qué significa una siniestralidad alta?
```

Respuesta esperada:

* Explicación conceptual.
* Fuente documental consultada.
* Interpretación general.
* Advertencia de que el valor debe analizarse según contexto.

---

### 9.2 Consultas analíticas

Estas consultas ejecutan análisis sobre datos estructurados en Parquet usando DuckDB.

Ejemplo:

```text id="n03baz"
Compara el promedio del indicador de siniestralidad por regional
```

Respuesta esperada:

* SQL ejecutado.
* Promedio por regional.
* Conteo de registros.
* Interpretación comparativa.

---

### 9.3 Consultas con cálculo de KPI

Estas consultas calculan diferencias, brechas o variaciones.

Ejemplo:

```text id="zja3qv"
Compara el promedio del indicador de siniestralidad por regional
```

Si hay al menos dos regionales, el sistema puede calcular:

```text id="y092gk"
Diferencia absoluta: 4.36 puntos.
Valor más alto: Bogotá.
```

---

### 9.4 Consultas con generación de PDF

Cuando el usuario pide un reporte, informe, documento o PDF, el sistema genera un archivo descargable.

Ejemplo:

```text id="el3qa8"
Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF
```

Respuesta esperada:

* Análisis textual.
* Herramientas ejecutadas.
* Archivo PDF generado.
* Botón de descarga en la interfaz.

---

### 9.5 Consultas sobre observabilidad

Estas consultas preguntan por las métricas del sistema.

Ejemplo:

```text id="4f6b79"
¿Qué métricas de observabilidad usa este sistema?
```

Respuesta esperada:

* Explicación de los KPIs.
* Uso de métricas como latencia, costo, score del juez y éxito de tools.
* Fuentes documentales si aplica.

---

## 10. Palabras clave que activan herramientas

El sistema identifica palabras clave dentro de la pregunta para decidir qué herramientas ejecutar.

---

### 10.1 Palabras que suelen activar análisis DuckDB

```text id="fycg78"
kpi
indicador
promedio
total
tasa
porcentaje
comparar
comparación
variación
mes
regional
costo
ingreso
siniestralidad
desempeño
```

---

### 10.2 Palabras que suelen activar generación PDF

```text id="hoppsd"
reporte
pdf
informe
descargar
documento
```

---

## 11. Interpretación de la respuesta

La respuesta del sistema puede incluir varias secciones.

---

### 11.1 Contexto recuperado mediante RAG

Esta sección muestra información obtenida de documentos.

Ejemplo:

```text id="1m8wu4"
Fuente: 03_guia_interpretacion_siniestralidad.txt
Score: 1.0
```

El score indica qué tan relevante fue el fragmento recuperado para la pregunta.

---

### 11.2 Resultado analítico consultado con DuckDB

Esta sección muestra el análisis ejecutado sobre datos estructurados.

Puede incluir:

* SQL ejecutado.
* Filas recuperadas.
* Promedios.
* Conteos.
* Mínimos.
* Máximos.
* Agrupaciones por regional o mes.

---

### 11.3 Cálculo adicional de KPI

Esta sección aparece cuando el sistema calcula un KPI derivado.

Ejemplo:

```text id="hv6b25"
Diferencia absoluta: 4.36 puntos.
Valor más alto: Bogotá.
```

---

### 11.4 Reporte PDF

Esta sección aparece cuando se genera un PDF.

Ejemplo:

```text id="vttbwb"
Se generó un reporte PDF en: data/reports/reporte_YYYYMMDD_HHMMSS.pdf
```

En la interfaz también aparecerá un botón para descargarlo.

---

## 12. Pestaña Métricas

La pestaña **Métricas** muestra el comportamiento del sistema.

Allí el usuario puede ver:

* Calidad de la respuesta.
* Velocidad del sistema.
* Éxito de herramientas.
* Costo estimado.
* Errores de cálculo.
* Cobertura RAG.
* Tokens estimados.
* Historial de métricas.

---

## 13. Los 8 KPIs principales

La prueba técnica exige mostrar 8 KPIs mínimos de observabilidad: éxito de tools, score del juez, TTL, costo por consulta, error de cálculos, latencia RAG, cobertura RAG y tokens promedio por sesión.

---

### 13.1 Tasa de éxito de tools

Mide el porcentaje de herramientas que se ejecutaron correctamente.

Ejemplo:

```text id="zrwb4l"
100%
```

Interpretación:

* Valor alto: las herramientas están funcionando bien.
* Valor bajo: una o más herramientas fallaron.

Umbral esperado:

```text id="f24pvf"
>= 95%
```

---

### 13.2 Score del agente juez

Mide la calidad de la respuesta en una escala de 0 a 10.

Ejemplo:

```text id="f332be"
8.0 / 10
```

Interpretación:

* Mayor o igual a 7.5: respuesta aceptable.
* Menor a 7.5: conviene revisar la respuesta.

Umbral esperado:

```text id="l48r5m"
>= 7.5 / 10
```

---

### 13.3 Time to Last Token

Mide el tiempo total desde que el usuario envía la pregunta hasta que recibe la respuesta completa.

Ejemplo:

```text id="td0qi1"
0.1285 s
```

Interpretación:

* Menor tiempo: mejor experiencia de usuario.
* Mayor tiempo: posible lentitud en RAG, tools o LLM.

Umbral esperado:

```text id="vwl4gj"
< 10 segundos
```

---

### 13.4 Costo estimado

Mide el costo estimado de la consulta cuando se usa Amazon Bedrock.

Ejemplo:

```text id="cqxhe9"
USD 0.000058
```

Interpretación:

* Valor bajo: consulta económica.
* Valor alto: se debe revisar el tamaño del contexto o el modelo usado.

Umbral esperado:

```text id="9xspnh"
< USD 0.05
```

---

### 13.5 Error en cálculos

Mide la proporción de errores detectados en consultas numéricas o KPIs.

Ejemplo:

```text id="vd7nsb"
0%
```

Interpretación:

* 0%: no se detectaron errores.
* Mayor a 0%: revisar DuckDB, datos Parquet o cálculo KPI.

Umbral esperado:

```text id="xza5w8"
< 3%
```

---

### 13.6 Latencia RAG

Mide el tiempo requerido para recuperar documentos relevantes.

Ejemplo:

```text id="342r1s"
0.0123 s
```

Interpretación:

* Latencia baja: recuperación documental rápida.
* Latencia alta: revisar tamaño del corpus o método de búsqueda.

Umbral esperado:

```text id="jtbd3j"
< 2 segundos
```

---

### 13.7 Cobertura RAG

Mide si el sistema encontró al menos un fragmento documental relevante.

Ejemplo:

```text id="d57kk7"
100%
```

Interpretación:

* 100%: se encontró contexto relevante.
* 0%: el sistema no encontró un fragmento suficientemente relacionado.

Umbral esperado:

```text id="4i1dn5"
>= 85%
```

---

### 13.8 Tokens por sesión

Mide la cantidad estimada de tokens consumidos por la conversación.

Ejemplo:

```text id="k1o1vs"
233
```

Interpretación:

* Más tokens pueden implicar mayor costo.
* Menos tokens pueden mejorar latencia y reducir gasto.
* Se debe monitorear y optimizar.

---

## 14. Pestaña Arquitectura

La pestaña **Arquitectura** muestra una explicación resumida del sistema.

Incluye:

* Flujo funcional.
* Componentes principales.
* Servicios AWS propuestos.
* Ruta de despliegue cloud.

Esta pestaña es útil para evaluadores técnicos o usuarios que quieren entender cómo se organiza la solución.

---

## 15. Cómo descargar un reporte PDF

Para generar un PDF, la pregunta debe incluir una palabra como:

```text id="ytmg1c"
reporte
pdf
informe
descargar
documento
```

Ejemplo:

```text id="juvtiv"
Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF
```

Después de ejecutar la consulta, aparecerá un botón:

```text id="w1f3cv"
Descargar reporte PDF
```

El usuario debe hacer clic en ese botón para guardar el archivo.

---

## 16. Casos de uso recomendados para demo

Para mostrar todas las capacidades del sistema, se recomienda usar esta consulta:

```text id="lp12ki"
Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF
```

Esta pregunta activa:

```text id="yjfacx"
RAG
DuckDB
KPI Calculator
PDF Generator
Judge Agent
Metrics Logger
```

También permite mostrar:

* Respuesta textual.
* Consulta SQL.
* KPI calculado.
* Reporte descargable.
* Dashboard con 8 métricas.
* Evaluación del juez.

---

## 17. Ejemplo de interpretación ejecutiva

Si el sistema responde que Bogotá tiene un promedio de siniestralidad de `72.63` y Antioquia de `68.27`, con una diferencia absoluta de `4.36` puntos, se puede interpretar así:

```text id="ccsohf"
Bogotá presenta un promedio de siniestralidad superior al de Antioquia.
La diferencia entre ambas regionales es de 4.36 puntos.
Dado que supera el umbral de referencia de 3 puntos mencionado en la metodología,
puede considerarse una posible alerta de desempeño que requiere revisión.
```

Esta interpretación debe entenderse como una lectura preliminar basada en los datos de prueba disponibles.

---

## 18. Comportamientos esperados

El usuario debe esperar que el sistema:

* Recupere documentos relevantes cuando existan.
* Ejecute análisis cuando la pregunta mencione indicadores, regionales, promedios o variaciones.
* Genere PDF solo si se solicita.
* Informe si no hay documentos disponibles.
* Informe si no existe el archivo Parquet.
* Muestre métricas después de cada consulta.
* Valide la respuesta con el agente juez.
* Registre el historial de métricas localmente.

---

## 19. Limitaciones del sistema

El sistema actual es un MVP funcional.

Limitaciones principales:

* Usa datos de prueba.
* Usa RAG local con TF-IDF.
* No implementa autenticación de usuarios.
* No tiene control de permisos por rol.
* El costo Bedrock es estimado cuando se ejecuta localmente.
* El juez puede operar en modo heurístico si Bedrock está desactivado.
* El vector store productivo AWS está documentado como ruta de mejora.
* CloudWatch está planteado como integración de despliegue AWS.
* La calidad de la respuesta depende del corpus documental disponible.
* Si la pregunta está fuera del dominio, puede recuperar contexto poco relevante.

---

## 20. Recomendaciones para mejores resultados

Para obtener mejores respuestas:

* Escribir preguntas claras.
* Incluir el indicador que se quiere analizar.
* Especificar si se quiere comparar por regional o por mes.
* Pedir explícitamente PDF si se necesita reporte.
* Revisar las fuentes RAG recuperadas.
* Consultar el score del agente juez.
* Verificar los resultados numéricos con el detalle de tools.
* Revisar las métricas si la respuesta tarda o falla.

Ejemplos de buenas preguntas:

```text id="sra765"
Compara el promedio del indicador de siniestralidad por regional.
```

```text id="ghdyx9"
Resume qué significa una siniestralidad entre 70 y 80.
```

```text id="aqbrf6"
Genera un informe PDF con la comparación de siniestralidad por regional.
```

---

## 21. Mensajes de error frecuentes

### 21.1 Backend no disponible

Mensaje posible:

```text id="b75vwe"
No fue posible consultar el backend
```

Qué significa:

El servidor FastAPI no está activo o no responde.

Qué hacer:

* Verificar que el backend esté corriendo.
* Revisar que la URL sea `http://127.0.0.1:8000/chat`.
* Reiniciar el backend.

---

### 21.2 No hay documentos cargados

Mensaje posible:

```text id="bp4ag2"
No hay documentos cargados en data/documents.
```

Qué significa:

El sistema no encontró documentos para el RAG.

Qué hacer:

* Agregar documentos en `data/documents`.
* Ejecutar el script de creación de corpus.
* Reiniciar la aplicación si es necesario.

---

### 21.3 No existe el archivo Parquet

Mensaje posible:

```text id="lg2chf"
No existe el archivo data/parquet/indicadores.parquet
```

Qué significa:

El sistema no encontró los datos estructurados.

Qué hacer:

* Ejecutar `scripts_create_sample_data.py`.
* Verificar que exista `data/parquet/indicadores.parquet`.

---

### 21.4 PDF no generado

Qué puede significar:

* La pregunta no incluyó “PDF”, “reporte” o “informe”.
* Hubo un problema en la carpeta `data/reports`.
* Falló la herramienta generadora de PDF.

Qué hacer:

* Pedir explícitamente un reporte PDF.
* Revisar el detalle de tools.
* Verificar permisos de escritura.

---

## 22. Validación rápida del sistema

Para validar que el sistema funciona correctamente:

1. Abrir Streamlit.
2. Ejecutar:

```text id="cfnb3t"
Compara el promedio del indicador de siniestralidad por regional y genera un reporte PDF
```

3. Confirmar que aparecen herramientas en estado OK.
4. Confirmar que se muestra una respuesta.
5. Confirmar que aparece el botón de descarga PDF.
6. Ir a la pestaña Métricas.
7. Confirmar que aparecen las 8 tarjetas KPI.
8. Revisar que el score del juez sea visible.
9. Revisar que existan fuentes RAG.
10. Revisar que el archivo PDF se genere en `data/reports`.

---

## 23. Glosario básico

### RAG

Mecanismo que permite que el sistema consulte documentos antes de responder.

### Tool

Herramienta externa que el sistema puede ejecutar, por ejemplo DuckDB, calculadora KPI o generador PDF.

### DuckDB

Motor de consulta SQL usado para analizar datos Parquet.

### Parquet

Formato de archivo usado para almacenar datos estructurados de forma eficiente.

### KPI

Indicador clave de desempeño.

### Agente juez

Componente que evalúa la calidad de la respuesta generada.

### TTL

Tiempo total que tarda el sistema en entregar una respuesta completa.

### Score RAG

Puntuación de relevancia de los documentos recuperados.

### Bedrock

Servicio de AWS para usar modelos de lenguaje como Claude, Titan o Llama.

---

## 24. Conclusión

El sistema permite consultar indicadores de desempeño en lenguaje natural, combinar evidencia documental con análisis estructurado, calcular KPIs, generar reportes PDF y monitorear la calidad del flujo mediante un dashboard de observabilidad.

Para el usuario final, el valor principal está en poder obtener respuestas analíticas trazables sin escribir código ni SQL directamente. Para el evaluador técnico, la interfaz permite comprobar que el sistema ejecuta un flujo agéntico completo con RAG, tools, agente juez y métricas.
