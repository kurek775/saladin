"""LLM factory with lazy imports — only the installed provider's package is needed."""

import logging

from langchain_core.language_models import BaseChatModel

from app.config import settings

logger = logging.getLogger(__name__)

# Known provider → default model mapping
DEFAULT_MODELS: dict[str, str] = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "gemini": "gemini-2.0-flash",
    "ollama": "llama3",
}


def create_llm(
    provider: str = "",
    model: str = "",
    api_key: str = "",
    base_url: str = "",
    max_tokens: int = 4096,
) -> BaseChatModel:
    """Create a LangChain chat model for the given provider.

    Falls back to global settings when arguments are empty.
    """
    provider = (provider or settings.LLM_PROVIDER).lower().strip()
    model = model or settings.LLM_MODEL or DEFAULT_MODELS.get(provider, "")

    if provider == "anthropic":
        return _create_anthropic(model, api_key, max_tokens)
    elif provider == "openai":
        return _create_openai(model, api_key, max_tokens)
    elif provider == "gemini":
        return _create_gemini(model, api_key, max_tokens)
    elif provider == "ollama":
        return _create_ollama(model, base_url)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider!r}")


def _create_anthropic(model: str, api_key: str, max_tokens: int) -> BaseChatModel:
    from langchain_anthropic import ChatAnthropic
    from app.core.key_context import get_request_keys

    key = api_key or get_request_keys().anthropic or settings.ANTHROPIC_API_KEY
    return ChatAnthropic(
        model=model,
        api_key=key,
        max_tokens=max_tokens,
    )


def _create_openai(model: str, api_key: str, max_tokens: int) -> BaseChatModel:
    from langchain_openai import ChatOpenAI
    from app.core.key_context import get_request_keys

    key = api_key or get_request_keys().openai or settings.OPENAI_API_KEY
    return ChatOpenAI(
        model=model,
        api_key=key,
        max_tokens=max_tokens,
    )


def _create_gemini(model: str, api_key: str, max_tokens: int) -> BaseChatModel:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from app.core.key_context import get_request_keys

    key = api_key or get_request_keys().google or settings.GOOGLE_API_KEY
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=key,
        max_output_tokens=max_tokens,
    )


def _create_ollama(model: str, base_url: str) -> BaseChatModel:
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=model,
        base_url=base_url or settings.OLLAMA_BASE_URL,
    )
