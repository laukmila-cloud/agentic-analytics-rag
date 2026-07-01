from tools.duckdb_tool import DuckDBTool


class AnalyticsWorker:
    def __init__(self):
        self.duckdb_tool = DuckDBTool()

    def analyze(self, question: str) -> dict:
        return self.duckdb_tool.run(question)