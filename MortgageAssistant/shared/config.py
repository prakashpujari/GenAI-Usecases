from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    env: str = "dev"
    aws_region: str = "us-east-1"

    s3_bucket: str
    dynamodb_table: str
    dynamodb_metadata_table: str
    kms_key_id: str

    opensearch_endpoint: str
    opensearch_index: str = "mortgage-docs"

    bedrock_region: str = "us-east-1"
    bedrock_embed_model: str
    bedrock_chat_model: str

    openai_api_key: str
    openai_chat_model: str
    openai_embed_model: str

    ingestion_service_url: str
    pii_service_url: str
    rag_service_url: str
    llm_router_url: str

    request_timeout_s: int = 20
    max_chunk_tokens: int = 700
    chunk_overlap_tokens: int = 120
    rate_limit_rps: int = 10


settings = Settings()
