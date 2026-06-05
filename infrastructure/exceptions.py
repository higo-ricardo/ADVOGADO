"""
exceptions.py — Hierarquia de exceções do Agente Jurídico.
"""


class AgentError(Exception):
    """Exceção base para todos os erros do agente."""
    pass


class LLMError(AgentError):
    """Erros relacionados a chamadas de LLM (OpenRouter, etc.)."""
    pass


class RAGError(AgentError):
    """Erros relacionados ao RAG (indexação, recuperação, embeddings)."""
    pass


class KnowledgeError(AgentError):
    """Erros relacionados à base de conhecimento (carregamento, arquivos)."""
    pass


class ValidationError(AgentError):
    """Erros de validação de dados de entrada."""
    pass


class ConfigurationError(AgentError):
    """Erros de configuração (API keys, paths, etc.)."""
    pass
