from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "local"
    aws_region: str = "us-east-1"
    use_bedrock: bool = False

    bedrock_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    bedrock_embedding_model_id: str = "amazon.titan-embed-text-v2:0"

    documents_path: str = "./data/documents"
    parquet_path: str = "./data/parquet"
    metrics_path: str = "./data/metrics.jsonl"
    reports_path: str = "./data/reports"
    vector_store_path: str = "./data/vector_store"

    class Config:
        env_file = ".env"


settings = Settings()