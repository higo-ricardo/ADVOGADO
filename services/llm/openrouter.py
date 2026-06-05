"""
openrouter.py — Implementação do provedor OpenRouter.
OpenRouter expõe API compatível com OpenAI.
"""
from __future__ import annotations

import os
from typing import Any, Generator

from openai import OpenAI

from infrastructure.config import config
from infrastructure.exceptions import ConfigurationError, LLMError
from services.llm.base import LLMProvider


class OpenRouterProvider(LLMProvider):
    """
    Provedor OpenRouter para chamadas de LLM.
    
    Suporta:
    - Modelo primário configurável
    - Fallback automático para modelos alternativos
    - Streaming e non-streaming
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
