"""
tests/services/llm/test_openrouter.py — Testes do provedor OpenRouter.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from infrastructure.exceptions import ConfigurationError, LLMError
from services.llm.openrouter import OpenRouterProvider


class TestOpenRouterProvider:
    """Testes da implementação OpenRouterProvider."""
    
    @patch('services.llm.openrouter.config')
    def test_initialization_with_api_key(self, mock_config):
        """Inicialização com API key funciona corretamente."""
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
        mock_config.APP_URL = "http://localhost"
        mock_config.APP_NAME = "Test App"
        mock_config.MODEL_PRIMARY = "test-model"
        mock_config.MODELS_FALLBACK = ["fallback-model"]
        mock_config.MAX_TOKENS = 1000
        
        provider = OpenRouterProvider(api_key="custom-key")
        
        assert provider.name == "OpenRouter"
        assert provider.is_available() is True
    
    @patch('services.llm.openrouter.config')
    def test_initialization_without_api_key_raises_error(self, mock_config):
        """Inicialização sem API key lança ConfigurationError."""
        mock_config.OPENROUTER_API_KEY = None
        
        with pytest.raises(ConfigurationError):
            OpenRouterProvider()
    
    @patch('services.llm.openrouter.config')
    @patch('services.llm.openrouter.OpenAI')
    def test_chat_completion_success(self, mock_openai_class, mock_config):
        """chat_completion retorna resposta com sucesso."""
        # Setup mocks
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
        mock_config.APP_URL = "http://localhost"
        mock_config.APP_NAME = "Test App"
        mock_config.MODEL_PRIMARY = "test-model"
        mock_config.MODELS_FALLBACK = []
        mock_config.MAX_TOKENS = 1000
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(delta=Mock(content="response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        provider = OpenRouterProvider()
        messages = [{"role": "user", "content": "Hello"}]
        
        result = provider.chat_completion(messages, stream=False)
        
        assert result == mock_response
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('services.llm.openrouter.config')
    @patch('services.llm.openrouter.OpenAI')
    def test_chat_completion_with_fallback(self, mock_openai_class, mock_config):
        """chat_completion usa fallback quando modelo primário falha."""
        # Setup mocks
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
        mock_config.APP_URL = "http://localhost"
        mock_config.APP_NAME = "Test App"
        mock_config.MODEL_PRIMARY = "primary-model"
        mock_config.MODELS_FALLBACK = ["fallback-model"]
        mock_config.MAX_TOKENS = 1000
        
        mock_client = Mock()
        mock_response = Mock()
        mock_client.chat.completions.create.side_effect = [
            Exception("Primary model failed"),  # Primeira tentativa falha
            mock_response  # Fallback funciona
        ]
        mock_openai_class.return_value = mock_client
        
        provider = OpenRouterProvider()
        messages = [{"role": "user", "content": "Hello"}]
        
        result = provider.chat_completion(messages, stream=False)
        
        assert result == mock_response
        assert mock_client.chat.completions.create.call_count == 2
    
    @patch('services.llm.openrouter.config')
    @patch('services.llm.openrouter.OpenAI')
    def test_chat_completion_all_failures_raises_error(self, mock_openai_class, mock_config):
        """chat_completion lança LLMError quando todos os modelos falham."""
        # Setup mocks
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
        mock_config.APP_URL = "http://localhost"
        mock_config.APP_NAME = "Test App"
        mock_config.MODEL_PRIMARY = "primary-model"
        mock_config.MODELS_FALLBACK = ["fallback-model"]
        mock_config.MAX_TOKENS = 1000
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("All models failed")
        mock_openai_class.return_value = mock_client
        
        provider = OpenRouterProvider()
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMError):
            provider.chat_completion(messages, stream=False)
    
    @patch('services.llm.openrouter.config')
    @patch('services.llm.openrouter.OpenAI')
    def test_chat_completion_stream_yields_content(self, mock_openai_class, mock_config):
        """chat_completion_stream yields chunks de conteúdo."""
        # Setup mocks
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
        mock_config.APP_URL = "http://localhost"
        mock_config.APP_NAME = "Test App"
        mock_config.MODEL_PRIMARY = "test-model"
        mock_config.MODELS_FALLBACK = []
        mock_config.MAX_TOKENS = 1000
        
        mock_client = Mock()
        mock_chunk1 = Mock()
        mock_chunk1.choices = [Mock(delta=Mock(content="Hello "))]
        mock_chunk2 = Mock()
        mock_chunk2.choices = [Mock(delta=Mock(content="world!"))]
        mock_chunk3 = Mock()
        mock_chunk3.choices = []  # Chunk vazio no final
        
        mock_client.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2, mock_chunk3])
        mock_openai_class.return_value = mock_client
        
        provider = OpenRouterProvider()
        messages = [{"role": "user", "content": "Hello"}]
        
        chunks = list(provider.chat_completion_stream(messages))
        
        assert chunks == ["Hello ", "world!"]
    
    @patch('services.llm.openrouter.config')
    def test_is_available_returns_true_with_key(self, mock_config):
        """is_available retorna True quando API key está presente."""
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
        mock_config.APP_URL = "http://localhost"
        mock_config.APP_NAME = "Test App"
        mock_config.MODEL_PRIMARY = "test-model"
        mock_config.MODELS_FALLBACK = []
        mock_config.MAX_TOKENS = 1000
        
        provider = OpenRouterProvider()
        assert provider.is_available() is True
    
    @patch('services.llm.openrouter.config')
    def test_name_property(self, mock_config):
        """Propriedade name retorna 'OpenRouter'."""
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
        mock_config.APP_URL = "http://localhost"
        mock_config.APP_NAME = "Test App"
        mock_config.MODEL_PRIMARY = "test-model"
        mock_config.MODELS_FALLBACK = []
        mock_config.MAX_TOKENS = 1000
        
        provider = OpenRouterProvider()
        assert provider.name == "OpenRouter"
