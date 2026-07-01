import os

import duckdb

from app.config import settings


class DuckDBTool:
    def run(self, question: str) -> dict:
        parquet_file = os.path.join(settings.parquet_path, "indicadores.parquet")

        if not os.path.exists(parquet_file):
            return {
                "success": False,
                "error": "No existe el archivo data/parquet/indicadores.parquet",
                "data": [],
            }

        try:
            query = self._question_to_sql(question, parquet_file)
            df = duckdb.query(query).to_df()

            return {
                "success": True,
                "sql": query,
                "data": df.to_dict(orient="records"),
            }

        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
                "data": [],
            }

    def _question_to_sql(self, question: str, parquet_file: str) -> str:
        q = question.lower()

        if "regional" in q:
            return f"""
            SELECT
                regional,
                COUNT(*) AS total_registros,
                ROUND(AVG(valor_indicador), 2) AS promedio_indicador
            FROM read_parquet('{parquet_file}')
            GROUP BY regional
            ORDER BY promedio_indicador DESC
            """

        if "mes" in q:
            return f"""
            SELECT
                mes,
                COUNT(*) AS total_registros,
                ROUND(AVG(valor_indicador), 2) AS promedio_indicador
            FROM read_parquet('{parquet_file}')
            GROUP BY mes
            ORDER BY mes
            """

        return f"""
        SELECT
            COUNT(*) AS total_registros,
            ROUND(AVG(valor_indicador), 2) AS promedio_indicador,
            ROUND(MIN(valor_indicador), 2) AS minimo,
            ROUND(MAX(valor_indicador), 2) AS maximo
        FROM read_parquet('{parquet_file}')
        """