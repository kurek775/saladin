from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Global LLM defaults
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "claude-sonnet-4-20250514"

    # Provider API keys
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # Ollama settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Legacy alias kept for backwards compatibility
    ANTHROPIC_MODEL: str = ""

    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    WS_HEARTBEAT_INTERVAL: int = 30
    MAX_REVISIONS: int = 3

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
