import os

import pandas as pd

os.makedirs("data/parquet", exist_ok=True)

df = pd.DataFrame(
    [
        {
            "mes": "2026-01",
            "regional": "Bogotá",
            "indicador": "siniestralidad",
            "valor_indicador": 72.4,
        },
        {
            "mes": "2026-01",
            "regional": "Antioquia",
            "indicador": "siniestralidad",
            "valor_indicador": 68.1,
        },
        {
            "mes": "2026-02",
            "regional": "Bogotá",
            "indicador": "siniestralidad",
            "valor_indicador": 75.2,
        },
        {
            "mes": "2026-02",
            "regional": "Antioquia",
            "indicador": "siniestralidad",
            "valor_indicador": 69.8,
        },
        {
            "mes": "2026-03",
            "regional": "Bogotá",
            "indicador": "siniestralidad",
            "valor_indicador": 70.3,
        },
        {
            "mes": "2026-03",
            "regional": "Antioquia",
            "indicador": "siniestralidad",
            "valor_indicador": 66.9,
        },
    ]
)

df.to_parquet("data/parquet/indicadores.parquet", index=False)

print("Archivo creado: data/parquet/indicadores.parquet")