"""
src/domain/interfaces.py — Definição de interfaces (Protocolos) para inversão de dependência.
"""
from __future__ import annotations

from abc import abstractmethod
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


class DatabaseProtocol(Protocol):
    """Protocolo para acesso a banco de dados."""

    def get_connection(self):
        ...

    def initialize_schema(self) -> None:
        ...


class VectorStoreProtocol(Protocol):
    """Protocolo para armazenamento vetorial."""

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


class KnowledgeRepositoryProtocol(Protocol):
    """Protocolo para repositório de conhecimento."""

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
