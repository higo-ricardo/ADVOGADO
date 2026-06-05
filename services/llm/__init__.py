"""
services.llm — Interfaces e implementações de provedores LLM.
"""
from services.llm.base import LLMProvider
from services.llm.openrouter import OpenRouterProvider

__all__ = ["LLMProvider", "OpenRouterProvider"]
