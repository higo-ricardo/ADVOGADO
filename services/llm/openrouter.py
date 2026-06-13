"""
services/llm/openrouter.py — Implementação do provedor OpenRouter.
OpenRouter expõe API compatível com OpenAI.
"""
from __future__ import annotations

import os
from typing import Any, Generator

from openai import OpenAI

from infrastructure.config import config
from infrastructure.exceptions import ConfigurationError, LLMError
from services.llm.base import LLMProvider
from services.llm.rate_limiter import get_rate_limiter, RateLimitConfig


# Metadados dos modelos suportados pelo OpenRouter
MODEL_SPECS: dict[str, dict[str, Any]] = {
    "openrouter/auto": {
        "max_tokens": 4096,
        "context_window": 128000,
        "supports_streaming": True,
        "supports_embeddings": False,
    },
    "anthropic/claude-3.5-sonnet": {
        "max_tokens": 8192,
        "context_window": 200000,
        "supports_streaming": True,
        "supports_embeddings": False,
    },
    "openai/gpt-4o": {
        "max_tokens": 4096,
        "context_window": 128000,
        "supports_streaming": True,
        "supports_embeddings": False,
    },
    "openai/gpt-4o-mini": {
        "max_tokens": 4096,
        "context_window": 128000,
        "supports_streaming": True,
        "supports_embeddings": False,
    },
    "google/gemini-2.0-flash": {
        "max_tokens": 8192,
        "context_window": 1048576,
        "supports_streaming": True,
        "supports_embeddings": False,
    },
}

DEFAULT_MODEL_SPEC = {
    "max_tokens": 4096,
    "context_window": 8192,
    "supports_streaming": True,
    "supports_embeddings": False,
}


class OpenRouterProvider(LLMProvider):
    """
    Provedor OpenRouter para chamadas de LLM.
    
    Suporta:
    - Modelo primário configurável
    - Fallback automático para modelos alternativos
    - Streaming e non-streaming
    - Rate limiting integrado
    - Embeddings via modelo dedicado (all-MiniLM-L6-v2 local)
    - Contagem de tokens via tiktoken
    """
    
    def __init__(self, api_key: str | None = None):
        """
        Inicializa o provider OpenRouter.
        
        Args:
            api_key: Chave de API (opcional, usa config se não fornecida)
        """
        self._api_key = api_key or config.OPENROUTER_API_KEY
        if not self._api_key:
            raise ConfigurationError(
                "OPENROUTER_API_KEY não configurada. "
                "Configure em .streamlit/secrets.toml ou variável de ambiente."
            )
        
        self._client = OpenAI(
            api_key=self._api_key,
            base_url=config.OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": config.APP_URL,
                "X-Title": config.APP_NAME,
            },
        )
        
        self._model_primary = config.MODEL_PRIMARY
        self._models_fallback = config.MODELS_FALLBACK
        self._max_tokens = config.MAX_TOKENS
        
        # Lazy loading do modelo de embeddings local
        self._embedding_model = None
        
        # Inicializa rate limiter com configuração da aplicação
        self._rate_limiter = get_rate_limiter()
    
    @property
    def name(self) -> str:
        return "OpenRouter"
    
    def is_available(self) -> bool:
        """Verifica se a API key está configurada."""
        return bool(self._api_key)
    
    def _try_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Tenta uma completion com um modelo específico."""
        # Aguarda rate limiter antes de fazer requisição
        if not self._rate_limiter.acquire(timeout=30.0):
            raise LLMError(
                "Rate limit excedido. Aguarde alguns segundos antes de tentar novamente."
            )
        
        return self._client.chat.completions.create(
            model=model,
            max_tokens=kwargs.get("max_tokens", self._max_tokens),
            stream=stream,
            messages=messages,
        )
    
    def chat_completion(
        self,
        messages: list[dict[str, str]],
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """
        Cria uma completion de chat com fallback automático.
        
        Tenta o modelo primário primeiro, depois os fallbacks em caso de erro.
        """
        erros = []
        modelos = [self._model_primary] + self._models_fallback
        
        for modelo in modelos:
            try:
                return self._try_completion(
                    model=modelo,
                    messages=messages,
                    stream=stream,
                    **kwargs,
                )
            except Exception as exc:
                erros.append((modelo, exc))
                continue
        
        # Se todos falharam, lança o último erro
        if erros:
            modelo, erro = erros[-1]
            raise LLMError(f"Falha ao chamar LLM (último modelo: {modelo}): {erro}")
        
        raise LLMError("Nenhum modelo disponível")
    
    def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        """
        Cria uma completion de chat com streaming.
        
        Yields:
            Chunks de texto da resposta
        """
        # Rate limiting já é aplicado no chat_completion
        stream = self.chat_completion(
            messages=messages,
            stream=True,
            **kwargs,
        )
        
        try:
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
        except Exception as exc:
            raise LLMError(f"Erro no streaming: {exc}")
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Gera embeddings vetoriais usando modelo local (all-MiniLM-L6-v2).
        
        O OpenRouter não expõe endpoint de embeddings, então usamos
        sentence_transformers local como fallback seguro e rápido.
        
        Args:
            texts: Lista de textos para gerar embeddings
        
        Returns:
            Lista de vetores (cada vetor é list[float])
        """
        try:
            if self._embedding_model is None:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            
            embeddings = self._embedding_model.encode(texts)
            return embeddings.tolist()
        except ImportError:
            raise LLMError(
                "sentence_transformers não instalado. "
                "Execute: pip install sentence-transformers"
            )
        except Exception as exc:
            raise LLMError(f"Erro ao gerar embeddings: {exc}")
    
    def count_tokens(self, text: str) -> int:
        """
        Conta tokens usando tiktoken (aproximação para o modelo ativo).
        
        Args:
            text: Texto para contar tokens
        
        Returns:
            Número estimado de tokens
        """
        try:
            import tiktoken
            try:
                encoding = tiktoken.encoding_for_model(self._model_primary)
            except KeyError:
                # Modelo não mapeado — usa encoding padrão GPT-4
                encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            # Fallback grosseiro: ~4 chars por token
            return len(text) // 4
    
    def get_model_info(self) -> dict[str, Any]:
        """
        Retorna metadados do modelo primário configurado.
        
        Returns:
            Dict com: max_tokens, context_window, supports_streaming,
            supports_embeddings, provider, model
        """
        spec = MODEL_SPECS.get(self._model_primary, DEFAULT_MODEL_SPEC)
        return {
            **spec,
            "provider": self.name,
            "model": self._model_primary,
        }
    
    def get_rate_limit_stats(self) -> dict:
        """
        Retorna estatísticas de uso do rate limiter.
        
        Returns:
            Dicionário com estatísticas de rate limiting
        """
        return self._rate_limiter.get_stats()
