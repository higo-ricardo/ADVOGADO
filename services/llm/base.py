"""
base.py — Interface abstrata para provedores LLM.
Define o contrato que todos os providers devem implementar.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generator


class LLMProvider(ABC):
    """
    Interface abstrata para provedores de LLM.
    
    Todos os providers (OpenRouter, OpenAI, Anthropic, etc.)
    devem implementar esta interface.
    """
    
    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict[str, str]],
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """
        Cria uma completion de chat.
        
        Args:
            messages: Lista de mensagens no formato OpenAI
            stream: Se True, retorna um generator para streaming
            **kwargs: Argumentos adicionais (max_tokens, temperature, etc.)
        
        Returns:
            Se stream=False: resposta completa
            Se stream=True: generator de chunks
        """
        pass
    
    @abstractmethod
    def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        """
        Cria uma completion de chat com streaming.
        
        Args:
            messages: Lista de mensagens no formato OpenAI
            **kwargs: Argumentos adicionais
        
        Yields:
            Chunks de texto da resposta
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica se o provider está disponível e configurado.
        
        Returns:
            True se estiver disponível, False caso contrário
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome do provider."""
        pass
