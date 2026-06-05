"""
retriever.py — Recuperação semântica para RAG.
Busca trechos relevantes da base de conhecimento usando similaridade de cosseno.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

from infrastructure.config import config
from infrastructure.exceptions import RAGError
from services.rag.indexer import DocumentIndexer


class SemanticRetriever:
    """
    Recuperador semântico para RAG.
    
    Responsabilidades:
    - Codificar consultas
    - Calcular similaridade com vetores do índice
    - Retornar trechos mais relevantes
    """
    
    def __init__(
        self,
        indexer: DocumentIndexer,
        model_name: str | None = None,
        top_k: int | None = None,
    ):
        """
        Inicializa o recuperador.
        
        Args:
            indexer: Instância do indexador com documentos já indexados
            model_name: Nome do modelo de embeddings
            top_k: Número de resultados a retornar
        """
        self.indexer = indexer
        self.model_name = model_name or config.RAG_MODEL_NAME
        self.top_k = top_k or config.RAG_TOP_K
        
        self._model: SentenceTransformer | None = None
    
    def _load_model(self) -> SentenceTransformer:
        """Carrega o modelo de embeddings."""
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception as exc:
                raise RAGError(f"Falha ao carregar modelo de embeddings: {exc}")
        return self._model
    
    def search(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Busca trechos relevantes para uma consulta.
        
        Args:
            query: Texto da consulta
            top_k: Número de resultados (sobrescreve default)
        
        Returns:
            Lista de dicts: [{id, texto, score}, ...]
        """
        if not self.indexer.is_indexed:
            return []
        
        k = top_k if top_k is not None else self.top_k
        modelo = self._load_model()
        vectors = self.indexer.vectors
        textos = self.indexer.textos
        ids = self.indexer.ids
        
        if vectors is None or len(textos) == 0:
            return []
        
        try:
            # Codifica a consulta
            query_vec = modelo.encode([query], normalize_embeddings=True)
            
            # Calcula similaridade de cosseno
            scores = (vectors @ query_vec[0]).astype(np.float32)
            
            # Obtém top-k índices
            k = min(k, len(scores))
            top_indices = np.argpartition(-scores, k - 1)[:k]
            top_indices = top_indices[np.argsort(-scores[top_indices])]
            
            # Constrói resultados
            resultados = []
            for rank, i in enumerate(top_indices):
                resultados.append({
                    "id": ids[i],
                    "texto": textos[i],
                    "score": float(scores[i]),
                    "rank": rank + 1,
                })
            
            return resultados
            
        except Exception as exc:
            raise RAGError(f"Falha na busca semântica: {exc}")
    
    def search_with_context(
        self,
        query: str,
        top_k: int | None = None,
        format_str: bool = True,
    ) -> str:
        """
        Busca e retorna contexto formatado como string.
        
        Args:
            query: Texto da consulta
            top_k: Número de resultados
            format_str: Se True, formata como string legível
        
        Returns:
            String com trechos concatenados
        """
        resultados = self.search(query, top_k=top_k)
        
        if not resultados:
            return "[Nenhum trecho relevante encontrado]"
        
        if format_str:
            return "\n\n".join(
                f"[Trecho {r['rank']}]\n{r['texto']}"
                for r in resultados
            )
        
        return "\n\n".join(r["texto"] for r in resultados)
