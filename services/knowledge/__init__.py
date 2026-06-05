"""
services.knowledge — Carregamento e repositório de conhecimento.
"""
from services.knowledge.loader import KnowledgeLoader
from services.knowledge.repository import KnowledgeRepository, MINUTA_POR_CODIGO

__all__ = ["KnowledgeLoader", "KnowledgeRepository", "MINUTA_POR_CODIGO"]
