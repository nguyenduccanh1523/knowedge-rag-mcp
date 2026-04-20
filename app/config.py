from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "knowledge-rag-mcp"
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8002
    app_log_level: str = "INFO"

    database_url: str

    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    embedding_dim: int = 384

    chunk_size: int = 900
    chunk_overlap: int = 150

    rerank_vector_weight: float = 0.65
    rerank_lexical_weight: float = 0.35

    mcp_server_name: str = "knowledge-rag-mcp"
    mcp_server_instructions: str = (
        "Knowledge RAG MCP server for finance evidence ingestion and hybrid retrieval."
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()