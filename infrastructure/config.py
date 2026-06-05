"""
config.py — Configuração centralizada do Agente Jurídico.
Usa variáveis de ambiente e pydantic-settings quando disponível.
"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configurações centralizadas do agente."""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    KNOWLEDGE_DIR = BASE_DIR / "knowledge"
    INDEX_DIR = BASE_DIR / "data" / "knowledge_index"
    
    # OpenRouter / LLM
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    APP_URL: str = "http://localhost:8501"
    APP_NAME: str = "Agente Juridico"
    
    # Modelos
    MODEL_PRIMARY: str = "openrouter/free"
    MODELS_FALLBACK: list = None
    MAX_TOKENS: int = 2048
    
    # RAG
    RAG_MODEL_NAME: str = "all-MiniLM-L6-v2"
    RAG_CHUNK_SIZE: int = 400
    RAG_CHUNK_OVERLAP: int = 80
    RAG_TOP_K: int = 4
    
    def __init__(self):
        self._load_from_env()
        if self.MODELS_FALLBACK is None:
            self.MODELS_FALLBACK = [
                "openai/gpt-4o-mini:free",
                "meta-llama/llama-4-maverick:free",
                "google/gemini-2.0-flash-exp:free",
            ]
    
    def _load_from_env(self):
        """Carrega configurações de variáveis de ambiente."""
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
        self.APP_URL = os.getenv("APP_URL", self.APP_URL)
        self.APP_NAME = os.getenv("APP_NAME", self.APP_NAME)
        self.MODEL_PRIMARY = os.getenv("LLM_MODEL_PRIMARY", self.MODEL_PRIMARY)
        self.MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", str(self.MAX_TOKENS)))
        self.RAG_MODEL_NAME = os.getenv("RAG_MODEL_NAME", self.RAG_MODEL_NAME)
        self.RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", str(self.RAG_CHUNK_SIZE)))
        self.RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", str(self.RAG_CHUNK_OVERLAP)))
        self.RAG_TOP_K = int(os.getenv("RAG_TOP_K", str(self.RAG_TOP_K)))
        
        # Garante que diretórios existem
        self.INDEX_DIR.mkdir(parents=True, exist_ok=True)


# Instância global
config = Config()
