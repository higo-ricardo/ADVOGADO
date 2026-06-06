"""
Repositório para gerenciamento de Fontes URL e Cache de Conhecimento.

Este módulo fornece operações para gerenciar fontes externas (URLs) 
e o cache de conhecimento processado para o sistema RAG.
"""

import json
import sqlite3
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime

from data.database import db_manager
from infrastructure.logging_config import get_logger

logger = get_logger(__name__)


class FonteURL:
    """Modelo de dados para uma Fonte URL."""
    
    def __init__(self, id: int, url: str, title: Optional[str] = None,
                 content_summary: Optional[str] = None, content_hash: Optional[str] = None,
                 category: Optional[str] = None, last_scraped_at: Optional[datetime] = None,
                 is_active: bool = True):
        self.id = id
        self.url = url
        self.title = title
        self.content_summary = content_summary
        self.content_hash = content_hash
        self.category = category
        self.last_scraped_at = last_scraped_at
        self.is_active = is_active

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'FonteURL':
        """Cria uma instância de FonteURL a partir de uma linha do banco de dados."""
        return cls(
            id=row['id'],
            url=row['url'],
            title=row['title'],
            content_summary=row['content_summary'],
            content_hash=row['content_hash'],
            category=row['category'],
            last_scraped_at=row['last_scraped_at'],
            is_active=bool(row['is_active'])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto FonteURL para um dicionário."""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'content_summary': self.content_summary,
            'content_hash': self.content_hash,
            'category': self.category,
            'last_scraped_at': str(self.last_scraped_at) if self.last_scraped_at else None,
            'is_active': self.is_active
        }


class KnowledgeCache:
    """Modelo de dados para um item no cache de conhecimento."""
    
    def __init__(self, id: int, source_type: str, source_id: Optional[int],
                 chunk_content: str, metadata: Optional[Dict[str, Any]] = None,
                 created_at: Optional[datetime] = None, embedding: Optional[bytes] = None):
        self.id = id
        self.source_type = source_type  # 'verbete_stf', 'verbete_stj', 'url', 'local_file'
        self.source_id = source_id
        self.chunk_content = chunk_content
        self.metadata = metadata or {}
        self.created_at = created_at
        self.embedding = embedding  # Armazenamento binário do vetor

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'KnowledgeCache':
        """Cria uma instância de KnowledgeCache a partir de uma linha do banco de dados."""
        metadata = json.loads(row['metadata']) if row['metadata'] else None
        return cls(
            id=row['id'],
            source_type=row['source_type'],
            source_id=row['source_id'],
            chunk_content=row['chunk_content'],
            metadata=metadata,
            created_at=row['created_at'],
            embedding=row['embedding']
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto KnowledgeCache para um dicionário."""
        return {
            'id': self.id,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'chunk_content': self.chunk_content,
            'metadata': self.metadata,
            'created_at': str(self.created_at) if self.created_at else None,
            'has_embedding': self.embedding is not None
        }


class KnowledgeRepository:
    """Repositório para operações com fontes URL e cache de conhecimento."""

    # ==================== Fontes URL ====================

    def add_fonte_url(self, url: str, title: Optional[str] = None,
                      content_summary: Optional[str] = None,
                      category: Optional[str] = None) -> FonteURL:
        """Adiciona ou atualiza uma fonte URL."""
        # Calcula hash do conteúdo para detecção de mudanças
        content_hash = hashlib.sha256((content_summary or '').encode()).hexdigest()
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verifica se já existe
            cursor.execute("SELECT id FROM fontes_url WHERE url = ?", (url,))
            existing = cursor.fetchone()
            
            if existing:
                # Atualiza
                cursor.execute("""
                    UPDATE fontes_url
                    SET title = ?, content_summary = ?, content_hash = ?,
                        category = ?, last_scraped_at = CURRENT_TIMESTAMP, is_active = 1
                    WHERE url = ?
                """, (title, content_summary, content_hash, category, url))
                fonte_id = existing[0]
            else:
                # Insere
                cursor.execute("""
                    INSERT INTO fontes_url (url, title, content_summary, content_hash, category)
                    VALUES (?, ?, ?, ?, ?)
                """, (url, title, content_summary, content_hash, category))
                
                fonte_id = cursor.lastrowid
        
        # Busca fora da transação para evitar lock
        return self.get_fonte_by_id(fonte_id)

    def get_fonte_by_id(self, fonte_id: int) -> Optional[FonteURL]:
        """Obtém uma fonte URL pelo ID."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fontes_url WHERE id = ?", (fonte_id,))
            row = cursor.fetchone()
            return FonteURL.from_row(row) if row else None

    def get_fonte_by_url(self, url: str) -> Optional[FonteURL]:
        """Obtém uma fonte URL pela URL."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fontes_url WHERE url = ?", (url,))
            row = cursor.fetchone()
            return FonteURL.from_row(row) if row else None

    def get_all_fontes(self, active_only: bool = True, 
                       category: Optional[str] = None) -> List[FonteURL]:
        """Obtém todas as fontes URL."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM fontes_url WHERE 1=1"
            params = []
            
            if active_only:
                query += " AND is_active = 1"
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY last_scraped_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [FonteURL.from_row(row) for row in rows]

    def deactivate_fonte(self, fonte_id: int) -> bool:
        """Desativa uma fonte URL."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE fontes_url SET is_active = 0 WHERE id = ?
            """, (fonte_id,))
            return cursor.rowcount > 0

    # ==================== Knowledge Cache ====================

    def add_cache_chunk(self, source_type: str, source_id: Optional[int],
                        chunk_content: str, metadata: Optional[Dict[str, Any]] = None,
                        embedding: Optional[bytes] = None) -> KnowledgeCache:
        """Adiciona um chunk ao cache de conhecimento."""
        metadata_json = json.dumps(metadata) if metadata else None
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO knowledge_cache (source_type, source_id, chunk_content, metadata, embedding)
                VALUES (?, ?, ?, ?, ?)
            """, (source_type, source_id, chunk_content, metadata_json, embedding))
            
            cache_id = cursor.lastrowid
        
        # Busca fora da transação para evitar lock
        return self.get_cache_by_id(cache_id)

    def get_cache_by_id(self, cache_id: int) -> Optional[KnowledgeCache]:
        """Obtém um item do cache pelo ID."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM knowledge_cache WHERE id = ?", (cache_id,))
            row = cursor.fetchone()
            return KnowledgeCache.from_row(row) if row else None

    def get_cache_by_source(self, source_type: str, 
                            source_id: Optional[int] = None) -> List[KnowledgeCache]:
        """Obtém todos os chunks de cache para uma determinada origem."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            if source_id is not None:
                cursor.execute("""
                    SELECT * FROM knowledge_cache
                    WHERE source_type = ? AND source_id = ?
                    ORDER BY created_at DESC
                """, (source_type, source_id))
            else:
                cursor.execute("""
                    SELECT * FROM knowledge_cache
                    WHERE source_type = ?
                    ORDER BY created_at DESC
                """, (source_type,))
            
            rows = cursor.fetchall()
            return [KnowledgeCache.from_row(row) for row in rows]

    def search_cache(self, search_term: str, limit: int = 20) -> List[KnowledgeCache]:
        """
        Busca no cache de conhecimento por termo.
        Nota: Para busca semântica real, seria necessário implementar busca vetorial.
        Esta é uma busca textual simples.
        """
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM knowledge_cache
                WHERE chunk_content LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (f'%{search_term}%', limit))
            
            rows = cursor.fetchall()
            return [KnowledgeCache.from_row(row) for row in rows]

    def clear_cache_for_source(self, source_type: str, 
                               source_id: Optional[int] = None) -> int:
        """
        Limpa o cache para uma determinada origem.
        Returns: Número de registros excluídos.
        """
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            if source_id is not None:
                cursor.execute("""
                    DELETE FROM knowledge_cache
                    WHERE source_type = ? AND source_id = ?
                """, (source_type, source_id))
            else:
                cursor.execute("""
                    DELETE FROM knowledge_cache
                    WHERE source_type = ?
                """, (source_type,))
            
            return cursor.rowcount

    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache de conhecimento."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total de chunks
            cursor.execute("SELECT COUNT(*) FROM knowledge_cache")
            stats['total_chunks'] = cursor.fetchone()[0]
            
            # Chunks por tipo de origem
            cursor.execute("""
                SELECT source_type, COUNT(*) as count
                FROM knowledge_cache
                GROUP BY source_type
            """)
            stats['by_source_type'] = {row['source_type']: row['count'] for row in cursor.fetchall()}
            
            # Chunks com embedding
            cursor.execute("""
                SELECT COUNT(*) FROM knowledge_cache
                WHERE embedding IS NOT NULL
            """)
            stats['chunks_with_embedding'] = cursor.fetchone()[0]
            
            return stats


# Instância singleton do repositório
knowledge_repository = KnowledgeRepository()
