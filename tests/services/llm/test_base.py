"""
tests/services/llm/test_base.py — Testes da interface abstrata LLMProvider.
"""
import pytest
from unittest.mock import Mock

from services.llm.base import LLMProvider


class ConcreteLLMProvider(LLMProvider):
    """Implementação concreta para testes."""
    
    def __init__(self, name: str = "TestProvider", available: bool = True):
        self._name = name
        self._available = available
    
    @property
    def name(self) -> str:
        return self._name
    
    def is_available(self) -> bool:
        return self._available
    
    def chat_completion(self, messages: list[dict[str, str]], stream: bool = False, **kwargs):
        if stream:
            return iter(["chunk1", "chunk2"])
        return "response"
    
    def chat_completion_stream(self, messages: list[dict[str, str]], **kwargs):
        yield "chunk1"
        yield "chunk2"


class TestLLMProviderInterface:
    """Testes da interface LLMProvider."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Não é possível instanciar a classe abstrata diretamente."""
        with pytest.raises(TypeError):
            LLMProvider()
    
    def test_concrete_implementation_works(self):
        """Implementação concreta funciona corretamente."""
        provider = ConcreteLLMProvider()
        
        assert provider.name == "TestProvider"
        assert provider.is_available() is True
        
        # Teste chat_completion non-stream
        messages = [{"role": "user", "content": "Hello"}]
        response = provider.chat_completion(messages, stream=False)
        assert response == "response"
    
    def test_chat_completion_stream_yields_chunks(self):
        """chat_completion_stream retorna generator com chunks."""
        provider = ConcreteLLMProvider()
        messages = [{"role": "user", "content": "Hello"}]
        
        chunks = list(provider.chat_completion_stream(messages))
        assert chunks == ["chunk1", "chunk2"]
    
    def test_is_available_false(self):
        """is_available retorna False quando configurado."""
        provider = ConcreteLLMProvider(available=False)
        assert provider.is_available() is False
    
    def test_name_property(self):
        """Propriedade name retorna o nome correto."""
        provider1 = ConcreteLLMProvider(name="OpenAI")
        provider2 = ConcreteLLMProvider(name="Anthropic")
        
        assert provider1.name == "OpenAI"
        assert provider2.name == "Anthropic"
