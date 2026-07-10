from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    external_llm_provider: str = Field(default="openai", alias="EXTERNAL_LLM_PROVIDER")
    external_llm_model: str = Field(default="gpt-4.1-mini", alias="EXTERNAL_LLM_MODEL")
    external_llm_api_key: str | None = Field(default=None, alias="EXTERNAL_LLM_API_KEY")

    ncbi_tool_name: str = Field(
        default="governed-biomedical-graphrag",
        alias="NCBI_TOOL_NAME",
    )
    ncbi_email: str = Field(default="your_email@example.com", alias="NCBI_EMAIL")
    ncbi_api_key: str | None = Field(default=None, alias="NCBI_API_KEY")

    vector_store_path: Path = Field(
        default=Path("builds/001-governed-biomedical-graphrag/data/vector_store"),
        alias="VECTOR_STORE_PATH",
    )
    audit_db_path: Path = Field(
        default=Path("builds/001-governed-biomedical-graphrag/data/audit/audit.duckdb"),
        alias="AUDIT_DB_PATH",
    )
    dailymed_cache_path: Path = Field(
        default=Path("builds/001-governed-biomedical-graphrag/data/cached_sources/dailymed"),
        alias="DAILYMED_CACHE_PATH",
    )
    pubmed_cache_path: Path = Field(
        default=Path("builds/001-governed-biomedical-graphrag/data/cached_sources/pubmed"),
        alias="PUBMED_CACHE_PATH",
    )

    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", alias="NEO4J_USERNAME")
    neo4j_password: str | None = Field(default=None, alias="NEO4J_PASSWORD")

    enable_pubmed: bool = Field(default=True, alias="ENABLE_PUBMED")
    enable_graph_validation: bool = Field(default=True, alias="ENABLE_GRAPH_VALIDATION")
    enable_strict_safety: bool = Field(default=True, alias="ENABLE_STRICT_SAFETY")
    enable_audit_logging: bool = Field(default=True, alias="ENABLE_AUDIT_LOGGING")


@lru_cache
def get_settings() -> Settings:
    return Settings()
