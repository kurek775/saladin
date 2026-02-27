import pytest
from app.config import Settings

def test_default_llm_provider():
    settings = Settings(_env_file=None) # Ensure no .env file is loaded
    assert settings.LLM_PROVIDER == "anthropic"

def test_default_llm_model():
    settings = Settings(_env_file=None)
    assert settings.LLM_MODEL == "claude-sonnet-4-20250514"

def test_default_storage_backend():
    settings = Settings(_env_file=None)
    assert settings.STORAGE_BACKEND == "memory"

def test_default_database_url():
    settings = Settings(_env_file=None)
    assert settings.DATABASE_URL == "sqlite:///./saladin.db"

def test_default_max_revisions():
    settings = Settings(_env_file=None)
    assert settings.MAX_REVISIONS == 3

def test_default_sandbox_mode():
    settings = Settings(_env_file=None)
    assert settings.SANDBOX_MODE == "local"

def test_default_use_queue():
    settings = Settings(_env_file=None)
    assert settings.USE_QUEUE is False

def test_default_cors_origins():
    settings = Settings(_env_file=None)
    assert settings.CORS_ORIGINS == ["http://localhost:5173"]
