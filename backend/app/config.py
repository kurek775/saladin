from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Global LLM defaults
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "claude-sonnet-4-20250514"

    # Provider API keys (optional with BYOK)
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # Ollama settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Legacy alias kept for backwards compatibility
    ANTHROPIC_MODEL: str = ""

    # Storage
    STORAGE_BACKEND: str = "memory"  # "memory" | "postgres"
    DATABASE_URL: str = "sqlite:///./saladin.db"

    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    WS_HEARTBEAT_INTERVAL: int = 30
    MAX_REVISIONS: int = 3

    # Redis / queue
    REDIS_URL: str = "redis://localhost:6379"
    USE_QUEUE: bool = False
    RATE_LIMIT_RPM: int = 60

    # Graph execution
    GRAPH_TIMEOUT_SECONDS: int = 600  # 10 minute global timeout per task

    # Self-improvement safety limits
    MAX_TASK_DEPTH: int = 3
    MAX_CHILD_TASKS_PER_TASK: int = 5
    MAX_TOTAL_AUTO_TASKS: int = 20
    ALLOW_AUTO_TASK_CREATION: bool = True

    # Coding / sandbox
    SANDBOX_MODE: str = "local"  # "local" | "docker" — local runs commands directly on host
    WORKSPACE_DIR: str = "./workspace"
    SANDBOX_IMAGE: str = "python:3.13-slim"
    SANDBOX_TIMEOUT: int = 30
    SANDBOX_NETWORK: bool = False
    SANDBOX_VOLUME_NAME: str = "saladin_workspace"

    # Broadcast loop
    BROADCAST_ERROR_DELAY: int = 5
    MAX_BROADCAST_ERROR_COUNT: int = 5

    # Sandbox image pre-pull
    SANDBOX_PULL_RETRIES: int = 3
    SANDBOX_PULL_RETRY_DELAY: int = 10

    # Worker Agent Tools
    DEFAULT_WORKER_TOOL_NAMES: list[str] = [
        "search_memory",
        "store_memory",
        "summarize_text",
        "read_file",
        "write_file",
        "list_files",
        "search_code",
        "run_command",
        "create_task",
        "append_improvement_note",
    ]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
