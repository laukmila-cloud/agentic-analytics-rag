import os

os.makedirs("data/documents", exist_ok=True)

documents = {
    "01_politica_indicadores.txt": """
Política de seguimiento de indicadores de desempeño

La organización realiza seguimiento mensual de indicadores de desempeño operativo y financiero.
Los indicadores deben analizarse por mes, regional y línea de negocio para identificar patrones, variaciones
y posibles alertas de gestión.

Uno de los indicadores principales es la siniestralidad. La siniestralidad permite evaluar la relación entre
los costos asociados a reclamaciones, atenciones o beneficios y los ingresos o recursos disponibles.

Una siniestralidad alta puede indicar mayor presión financiera, aumento de costos operativos,
incremento de reclamaciones o deterioro del desempeño técnico. Una siniestralidad baja puede indicar
mejor control del riesgo, eficiencia operativa o menor utilización de servicios.

Los indicadores regionales deben compararse usando promedios, variaciones mensuales, brechas absolutas
y umbrales definidos por la organización.
""",
    "02_metodologia_kpis.txt": """
Metodología para cálculo de KPIs analíticos

Los KPIs deben calcularse con fuentes estructuradas y trazables. Para análisis ejecutivo se recomienda
calcular promedio del indicador, mínimo, máximo, variación porcentual, brecha absoluta entre regionales
y número de registros considerados.

La variación porcentual se calcula como:
valor actual menos valor anterior, dividido por el valor anterior, multiplicado por cien.

La brecha absoluta entre dos regionales se calcula restando el valor del segundo grupo al valor del primer grupo.
Cuando la brecha es positiva, el primer grupo tiene un indicador mayor. Cuando la brecha es negativa,
el segundo grupo tiene un indicador mayor.

En indicadores de siniestralidad, una diferencia mayor a 3 puntos porcentuales entre regionales debe revisarse
como una posible alerta de desempeño, especialmente si se mantiene durante varios meses consecutivos.
""",
    "03_guia_interpretacion_siniestralidad.txt": """
Guía de interpretación de siniestralidad

La siniestralidad es un indicador crítico en organizaciones de compensación, aseguramiento o beneficios.
Representa la proporción de costos frente a ingresos, aportes o recursos disponibles.

Una siniestralidad entre 60 y 70 puede interpretarse como rango controlado, dependiendo del contexto operativo.
Una siniestralidad entre 70 y 80 requiere seguimiento porque puede reflejar incremento en costos,
uso intensivo de servicios o cambios en el comportamiento de la población afiliada.
Una siniestralidad superior a 80 puede representar una alerta de sostenibilidad financiera.

La interpretación no debe basarse en un único valor aislado. Debe revisarse la tendencia mensual,
la comparación por regional, el volumen de registros y las condiciones particulares de cada territorio.
""",
    "04_lineamientos_reporte_ejecutivo.txt": """
Lineamientos para reportes ejecutivos

Los reportes ejecutivos deben presentar los hallazgos de forma clara, trazable y accionable.
Toda respuesta analítica debe incluir la pregunta del usuario, los datos usados, las fuentes documentales
consultadas, los cálculos ejecutados y una síntesis interpretativa.

Cuando el sistema genere un reporte PDF, debe incluir el contexto recuperado por RAG, los resultados de
la consulta analítica, la interpretación de KPIs y la evaluación del agente juez.

Las métricas mínimas de observabilidad del sistema incluyen tiempo total de respuesta, tasa de éxito de tools,
latencia del pipeline RAG, número de chunks recuperados, score del juez, tokens estimados y costo estimado
por consulta.

El reporte debe advertir cuando la respuesta es preliminar, cuando el corpus no contiene suficiente información
o cuando los datos estructurados no permiten responder con precisión.
""",
}

for filename, content in documents.items():
    path = os.path.join("data/documents", filename)

    with open(path, "w", encoding="utf-8") as file:
        file.write(content.strip())

print("Corpus RAG creado en data/documents")
print("Documentos creados:")
for filename in documents:
    print(f"- {filename}")