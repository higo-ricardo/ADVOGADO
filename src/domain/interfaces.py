"""
src/domain/interfaces.py — Definição de interfaces (Protocolos) para inversão de dependência.

Este módulo define os contratos que os serviços devem implementar,
permitindo que a camada de aplicação dependa apenas de abstrações.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import abstractcontextmanager
from typing import Any, Generator, Protocol


# ============================================================================
# Interfaces de Serviços Externos (LLM, Vector Store, etc.)
# ============================================================================

class LLMProviderProtocol(Protocol):
    """Protocolo para provedores de LLM."""
    
    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict[str, str]],
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Cria uma completion de chat."""
        pass
    
    @abstractmethod
    def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        """Cria uma completion de chat com streaming."""
        pass
    
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Gera embeddings vetoriais para uma lista de textos."""
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Conta quantos tokens um texto gera no modelo ativo."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        """Retorna metadados do modelo (max_tokens, context_window, etc)."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o provider está disponível."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome do provider."""
        pass


class DatabaseProtocol(Protocol):
    """Protocolo para acesso a banco de dados."""
    
    @abstractcontextmanager
    def get_connection(self):
        """Context manager que retorna uma conexão SQLite."""
        ...
    
    def initialize_schema(self) -> None:
        """Cria as tabelas necessárias se ainda não existirem."""
        ...


class VectorStoreProtocol(Protocol):
    """Protocolo para armazenamento vetorial."""
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Busca documentos similares."""
        pass
    
    @abstractmethod
    def add_documents(self, documents: dict[str, str]) -> int:
        """Adiciona documentos ao índice."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reinicia o índice."""
        pass
    
    @property
    @abstractmethod
    def is_indexed(self) -> bool:
        """Verifica se há documentos indexados."""
        pass


class KnowledgeRepositoryProtocol(Protocol):
    """Protocolo para repositório de conhecimento."""
    
    @abstractmethod
    def get_minuta_por_codigo(self, codigo: str) -> str:
        """Obtém minuta específica por código."""
        pass
    
    @abstractmethod
    def get_estilo(self) -> str:
        """Obtém diretrizes de estilo."""
        pass
    
    @abstractmethod
    def get_minuta_base(self) -> str:
        """Obtém minuta base de formatação."""
        pass
    
    @abstractmethod
    def get_fontes(self) -> str:
        """Obtém fontes normativas."""
        pass
    
    @abstractmethod
    def build_contexto_estagiario(self, codigo: str) -> str:
        """Constrói contexto para o estagiário."""
        pass
    
    @abstractmethod
    def get_system_estagiario(self) -> str:
        """Obtém prompt de sistema do estagiário."""
        pass
    
    @abstractmethod
    def get_system_advogado(self) -> str:
        """Obtém prompt de sistema do advogado."""
        pass


# ============================================================================
# Interface de Repositório de Estado
# ============================================================================

class StateRepositoryProtocol(Protocol):
    """Protocolo para persistência de estado."""
    
    @abstractmethod
    def save(self, state_id: str, state_data: dict[str, Any]) -> bool:
        """Salva estado."""
        pass
    
    @abstractmethod
    def load(self, state_id: str) -> dict[str, Any] | None:
        """Carrega estado."""
        pass
    
    @abstractmethod
    def delete(self, state_id: str) -> bool:
        """Remove estado."""
        pass


# ============================================================================
# Classes Base Abstratas (para implementação concreta)
# ============================================================================

class LLMProviderBase(ABC):
    """Classe base abstrata para provedores LLM."""
    
    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict[str, str]],
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        pass
    
    @abstractmethod
    def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        pass
    
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass


class VectorStoreBase(ABC):
    """Classe base abstrata para armazenamento vetorial."""
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        pass
    
    @abstractmethod
    def add_documents(self, documents: dict[str, str]) -> int:
        pass
    
    @abstractmethod
    def reset(self) -> None:
        pass
    
    @property
    @abstractmethod
    def is_indexed(self) -> bool:
        pass


class KnowledgeRepositoryBase(ABC):
    """Classe base abstrata para repositório de conhecimento."""
    
    @abstractmethod
    def get_minuta_por_codigo(self, codigo: str) -> str:
        pass
    
    @abstractmethod
    def get_estilo(self) -> str:
        pass
    
    @abstractmethod
    def get_minuta_base(self) -> str:
        pass
    
    @abstractmethod
    def get_fontes(self) -> str:
        pass
    
    @abstractmethod
    def build_contexto_estagiario(self, codigo: str) -> str:
        pass
    
    @abstractmethod
    def get_system_estagiario(self) -> str:
        pass
    
    @abstractmethod
    def get_system_advogado(self) -> str:
        pass
