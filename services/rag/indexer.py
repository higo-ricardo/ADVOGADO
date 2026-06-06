"""
indexer.py — Indexação de documentos para RAG.
Indexa arquivos .md da knowledge base com embeddings locais.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

from infrastructure.config import config
from infrastructure.exceptions import RAGError, KnowledgeError


class DocumentIndexer:
    """
    Indexador de documentos para RAG.
    
    Responsabilidades:
    - Carregar modelo de embeddings
    - Dividir documentos em chunks
    - Criar vetores de embeddings
    - Gerenciar índice em memória
    """
    
    def __init__(
        self,
        model_name: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        """
        Inicializa o indexador.
        
        Args:
            model_name: Nome do modelo de embeddings
            chunk_size: Tamanho de cada chunk em palavras
            chunk_overlap: Sobreposição entre chunks
        """
        self.model_name = model_name or config.RAG_MODEL_NAME
        self.chunk_size = chunk_size or config.RAG_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.RAG_CHUNK_OVERLAP
        
        self._model: "SentenceTransformer | None" = None
        self._vectors: np.ndarray | None = None
        self._ids: list[str] = []
        self._textos: list[str] = []
        self._indexed = False
    
    def _load_model(self) -> "SentenceTransformer":
        """Carrega o modelo de embeddings."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as exc:
                raise RAGError(f"Falha ao carregar modelo de embeddings: {exc}")
        return self._model
    
    def _chunk_text(self, text: str) -> list[str]:
        """Divide texto em chunks com sobreposição."""
        if not text.strip():
            return []
        
        words = text.split()
        chunks: list[str] = []
        i = 0
        
        while i < len(words):
            chunk = " ".join(words[i : i + self.chunk_size])
            chunks.append(chunk)
            i += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def index_documents(
        self,
        documents: dict[str, str],
        force_rebuild: bool = False,
    ) -> int:
        """
        Indexa documentos.
        
        Args:
            documents: Dict {id_documento: conteudo_texto}
            force_rebuild: Se True, reconstrói índice existente
        
        Returns:
            Número de chunks indexados
        """
        if self._indexed and not force_rebuild:
            return len(self._textos)
        
        modelo = self._load_model()
        textos: list[str] = []
        ids: list[str] = []
        
        for doc_id, content in documents.items():
            chunks = self._chunk_text(content)
            for i, chunk in enumerate(chunks):
                textos.append(chunk)
                ids.append(f"{doc_id}::{i}")
        
        if not textos:
            self._vectors = np.zeros((0, 384), dtype=np.float32)
            self._indexed = True
            return 0
        
        try:
            embeddings = modelo.encode(textos, normalize_embeddings=True)
            self._vectors = np.array(embeddings, dtype=np.float32)
            self._ids = ids
            self._textos = textos
            self._indexed = True
        except Exception as exc:
            raise RAGError(f"Falha ao criar embeddings: {exc}")
        
        return len(textos)
    
    @property
    def is_indexed(self) -> bool:
        """Verifica se o índice foi construído."""
        return self._indexed
    
    @property
    def vector_count(self) -> int:
        """Retorna número de vetores no índice."""
        return len(self._textos) if self._vectors is not None else 0
    
    @property
    def vectors(self) -> np.ndarray | None:
        """Retorna matriz de vetores."""
        return self._vectors
    
    @property
    def ids(self) -> list[str]:
        """Retorna lista de IDs."""
        return self._ids
    
    @property
    def textos(self) -> list[str]:
        """Retorna lista de textos."""
        return self._textos
    
    def reset(self) -> None:
        """Reseta o índice."""
        self._vectors = None
        self._ids = []
        self._textos = []
        self._indexed = False
