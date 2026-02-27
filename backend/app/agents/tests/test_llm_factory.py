
import pytest
from unittest.mock import patch, MagicMock
from backend.app.agents.llm_factory import create_llm, DEFAULT_MODELS
from backend.app.core.key_context import KeyContext # Import KeyContext for mocking

# Fixture for mocking settings
@pytest.fixture
def mock_settings():
    with patch('backend.app.config.settings') as mock_s:
        mock_s.LLM_PROVIDER = ""
        mock_s.LLM_MODEL = ""
        mock_s.ANTHROPIC_API_KEY = "settings_anthropic_key"
        mock_s.OPENAI_API_KEY = "settings_openai_key"
        mock_s.GOOGLE_API_KEY = "settings_google_key"
        mock_s.OLLAMA_BASE_URL = "http://localhost:11434"
        yield mock_s

# Fixture for mocking get_request_keys
@pytest.fixture
def mock_get_request_keys():
    with patch('backend.app.agents.llm_factory.get_request_keys') as mock_grk:
        mock_grk.return_value = KeyContext(
            anthropic="request_anthropic_key",
            openai="request_openai_key",
            google="request_google_key",
        )
        yield mock_grk

# --- Test create_llm with various providers and fallback logic ---

@patch('backend.app.agents.llm_factory.ChatAnthropic')
def test_create_llm_anthropic(mock_chat_anthropic, mock_settings, mock_get_request_keys):
    mock_settings.LLM_PROVIDER = "anthropic"
    mock_settings.LLM_MODEL = "claude-3-opus"

    # Test with arguments
    llm = create_llm(provider="anthropic", model="claude-arg", api_key="arg_key", max_tokens=1000)
    mock_chat_anthropic.assert_called_once_with(model="claude-arg", api_key="arg_key", max_tokens=1000)
    assert isinstance(llm, MagicMock)
    mock_chat_anthropic.reset_mock()

    # Test with request keys
    llm = create_llm(provider="anthropic")
    mock_chat_anthropic.assert_called_once_with(model="claude-3-opus", api_key="request_anthropic_key", max_tokens=4096)
    mock_chat_anthropic.reset_mock()

    # Test with settings keys (no request key)
    mock_get_request_keys.return_value.anthropic = ""
    llm = create_llm(provider="anthropic")
    mock_chat_anthropic.assert_called_once_with(model="claude-3-opus", api_key="settings_anthropic_key", max_tokens=4096)
    mock_chat_anthropic.reset_mock()

    # Test with default model (no model in args/settings)
    mock_settings.LLM_MODEL = ""
    llm = create_llm(provider="anthropic")
    mock_chat_anthropic.assert_called_once_with(model=DEFAULT_MODELS["anthropic"], api_key="settings_anthropic_key", max_tokens=4096)

@patch('backend.app.agents.llm_factory.ChatOpenAI')
def test_create_llm_openai(mock_chat_openai, mock_settings, mock_get_request_keys):
    mock_settings.LLM_PROVIDER = "openai"
    mock_settings.LLM_MODEL = "gpt-3.5-turbo"

    # Test with arguments
    llm = create_llm(provider="openai", model="gpt-arg", api_key="arg_key", max_tokens=2000)
    mock_chat_openai.assert_called_once_with(model="gpt-arg", api_key="arg_key", max_tokens=2000)
    mock_chat_openai.reset_mock()

    # Test with request keys
    llm = create_llm(provider="openai")
    mock_chat_openai.assert_called_once_with(model="gpt-3.5-turbo", api_key="request_openai_key", max_tokens=4096)
    mock_chat_openai.reset_mock()

    # Test with settings keys
    mock_get_request_keys.return_value.openai = ""
    llm = create_llm(provider="openai")
    mock_chat_openai.assert_called_once_with(model="gpt-3.5-turbo", api_key="settings_openai_key", max_tokens=4096)
    mock_chat_openai.reset_mock()

    # Test with default model
    mock_settings.LLM_MODEL = ""
    llm = create_llm(provider="openai")
    mock_chat_openai.assert_called_once_with(model=DEFAULT_MODELS["openai"], api_key="settings_openai_key", max_tokens=4096)

@patch('backend.app.agents.llm_factory.ChatGoogleGenerativeAI')
def test_create_llm_gemini(mock_chat_gemini, mock_settings, mock_get_request_keys):
    mock_settings.LLM_PROVIDER = "gemini"
    mock_settings.LLM_MODEL = "gemini-1.5-pro"

    # Test with arguments
    llm = create_llm(provider="gemini", model="gemini-arg", api_key="arg_key", max_tokens=3000)
    mock_chat_gemini.assert_called_once_with(model="gemini-arg", google_api_key="arg_key", max_output_tokens=3000)
    mock_chat_gemini.reset_mock()

    # Test with request keys
    llm = create_llm(provider="gemini")
    mock_chat_gemini.assert_called_once_with(model="gemini-1.5-pro", google_api_key="request_google_key", max_output_tokens=4096)
    mock_chat_gemini.reset_mock()

    # Test with settings keys
    mock_get_request_keys.return_value.google = ""
    llm = create_llm(provider="gemini")
    mock_chat_gemini.assert_called_once_with(model="gemini-1.5-pro", google_api_key="settings_google_key", max_output_tokens=4096)
    mock_chat_gemini.reset_mock()

    # Test with default model
    mock_settings.LLM_MODEL = ""
    llm = create_llm(provider="gemini")
    mock_chat_gemini.assert_called_once_with(model=DEFAULT_MODELS["gemini"], google_api_key="settings_google_key", max_output_tokens=4096)

@patch('backend.app.agents.llm_factory.ChatOllama')
def test_create_llm_ollama(mock_chat_ollama, mock_settings, mock_get_request_keys):
    # Ollama doesn't use api_key or get_request_keys for key management, only base_url
    mock_settings.LLM_PROVIDER = "ollama"
    mock_settings.LLM_MODEL = "mistral"

    # Test with arguments
    llm = create_llm(provider="ollama", model="llama2", base_url="http://custom-ollama:11434")
    mock_chat_ollama.assert_called_once_with(model="llama2", base_url="http://custom-ollama:11434")
    mock_chat_ollama.reset_mock()

    # Test with settings base_url
    llm = create_llm(provider="ollama")
    mock_chat_ollama.assert_called_once_with(model="mistral", base_url="http://localhost:11434")
    mock_chat_ollama.reset_mock()

    # Test with default model
    mock_settings.LLM_MODEL = ""
    llm = create_llm(provider="ollama")
    mock_chat_ollama.assert_called_once_with(model=DEFAULT_MODELS["ollama"], base_url="http://localhost:11434")

def test_create_llm_unsupported_provider(mock_settings, mock_get_request_keys):
    with pytest.raises(ValueError, match="Unsupported LLM provider: 'unsupported'"):
        create_llm(provider="unsupported")

def test_create_llm_provider_from_settings(mock_settings, mock_get_request_keys):
    # Ensure provider can be picked from settings if not given in args
    mock_settings.LLM_PROVIDER = "openai"
    mock_settings.LLM_MODEL = "gpt-3.5-turbo"
    with patch('backend.app.agents.llm_factory.ChatOpenAI') as mock_chat_openai:
        create_llm()
        mock_chat_openai.assert_called_once()

def test_create_llm_provider_and_model_case_insensitivity(mock_settings, mock_get_request_keys):
    mock_settings.LLM_PROVIDER = "ANTHROPIC"
    mock_settings.LLM_MODEL = "CLAUDE-3-SONNET"
    with patch('backend.app.agents.llm_factory.ChatAnthropic') as mock_chat_anthropic:
        create_llm(provider="  AnThRoPiC  ", model="  ClAuDe-3-SoNnEt  ")
        mock_chat_anthropic.assert_called_once_with(model="  ClAuDe-3-SoNnEt  ", api_key="request_anthropic_key", max_tokens=4096)

def test_create_llm_max_tokens_default(mock_settings, mock_get_request_keys):
    mock_settings.LLM_PROVIDER = "openai"
    with patch('backend.app.agents.llm_factory.ChatOpenAI') as mock_chat_openai:
        create_llm(provider="openai")
        mock_chat_openai.assert_called_once_with(model=DEFAULT_MODELS["openai"], api_key="request_openai_key", max_tokens=4096)

