"""
Repositório para gerenciamento de Verbetes de Jurisprudência (STF e STJ).

Este módulo fornece operações para buscar e gerenciar verbetes das cortes superiores,
essenciais para o sistema RAG jurídico.
"""

import json
import sqlite3
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, date

from infrastructure.logging_config import get_logger

if TYPE_CHECKING:
    from src.domain.interfaces import DatabaseProtocol

logger = get_logger(__name__)


class Verbete:
    """Modelo de dados para um Verbete de Jurisprudência."""
    
    def __init__(self, id: int, tema: str, resumo: str, 
                 keywords: Optional[str] = None, source_url: Optional[str] = None,
                 date_decision: Optional[date] = None, full_text: Optional[str] = None,
                 indexed_at: Optional[datetime] = None, court: str = 'STF'):
        self.id = id
        self.tema = tema
        self.resumo = resumo
        self.keywords = keywords
        self.source_url = source_url
        self.date_decision = date_decision
        self.full_text = full_text
        self.indexed_at = indexed_at
        self.court = court  # 'STF' ou 'STJ'

    @classmethod
    def from_row(cls, row: sqlite3.Row, court: str) -> 'Verbete':
        """Cria uma instância de Verbete a partir de uma linha do banco de dados."""
        return cls(
            id=row['id'],
            tema=row['tema'],
            resumo=row['resumo'],
            keywords=row['keywords'],
            source_url=row['source_url'],
            date_decision=row['date_decision'],
            full_text=row['full_text'],
            indexed_at=row['indexed_at'],
            court=court
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto Verbete para um dicionário."""
        return {
            'id': self.id,
            'tema': self.tema,
            'resumo': self.resumo,
            'keywords': self.keywords.split(',') if self.keywords else [],
            'source_url': self.source_url,
            'date_decision': str(self.date_decision) if self.date_decision else None,
            'full_text': self.full_text,
            'indexed_at': str(self.indexed_at) if self.indexed_at else None,
            'court': self.court
        }


class VerbetesRepository:
    """Repositório para operações com verbetes do STF e STJ."""

    def __init__(self, db: "DatabaseProtocol | None" = None):
        if db is not None:
            self._db = db
        else:
            from data.database import db_manager
            self._db = db_manager

    def add_stf_verbete(self, tema: str, resumo: str, 
                        keywords: Optional[List[str]] = None,
                        source_url: Optional[str] = None,
                        date_decision: Optional[date] = None,
                        full_text: Optional[str] = None) -> Verbete:
        """Adiciona um novo verbete do STF."""
        return self._add_verbete('STF', tema, resumo, keywords, source_url, 
                                  date_decision, full_text)

    def add_stj_verbete(self, tema: str, resumo: str, 
                        keywords: Optional[List[str]] = None,
                        source_url: Optional[str] = None,
                        date_decision: Optional[date] = None,
                        full_text: Optional[str] = None) -> Verbete:
        """Adiciona um novo verbete do STJ."""
        return self._add_verbete('STJ', tema, resumo, keywords, source_url, 
                                  date_decision, full_text)

    def _add_verbete(self, court: str, tema: str, resumo: str,
                     keywords: Optional[List[str]], source_url: Optional[str],
                     date_decision: Optional[date], full_text: Optional[str]) -> Verbete:
        """Método interno para adicionar verbete."""
        table_name = 'verbetes_stf' if court == 'STF' else 'verbetes_stj'
        keywords_str = ','.join(keywords) if keywords else None
        
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {table_name} (tema, resumo, keywords, source_url, date_decision, full_text)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (tema, resumo, keywords_str, source_url, date_decision, full_text))
            
            verbete_id = cursor.lastrowid
        
        # Busca fora da transação para evitar lock
        return self.get_by_id(verbete_id, court)

    def get_by_id(self, verbete_id: int, court: str) -> Optional[Verbete]:
        """Obtém um verbete pelo ID e corte."""
        table_name = 'verbetes_stf' if court == 'STF' else 'verbetes_stj'
        
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (verbete_id,))
            row = cursor.fetchone()
            return Verbete.from_row(row, court) if row else None

    def search_by_theme(self, theme: str, court: Optional[str] = None, 
                        limit: int = 10) -> List[Verbete]:
        """
        Busca verbetes por tema ou palavras-chave.
        
        Args:
            theme: Termo de busca (busca parcial no tema e keywords).
            court: Filtra por corte ('STF', 'STJ' ou None para ambos).
            limit: Limite de resultados.
        """
        results = []
        
        courts_to_search = [court] if court else ['STF', 'STJ']
        
        for c in courts_to_search:
            table_name = 'verbetes_stf' if c == 'STF' else 'verbetes_stj'
            
            with self._db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT * FROM {table_name}
                    WHERE tema LIKE ? OR keywords LIKE ?
                    ORDER BY indexed_at DESC
                    LIMIT ?
                """, (f'%{theme}%', f'%{theme}%', limit))
                
                rows = cursor.fetchall()
                results.extend([Verbete.from_row(row, c) for row in rows])
        
        return results[:limit]  # Garante o limite total

    def get_all(self, court: Optional[str] = None, limit: int = 100) -> List[Verbete]:
        """Obtém todos os verbetes, opcionalmente filtrados por corte."""
        results = []
        courts_to_search = [court] if court else ['STF', 'STJ']
        
        for c in courts_to_search:
            table_name = 'verbetes_stf' if c == 'STF' else 'verbetes_stj'
            
            with self._db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT * FROM {table_name}
                    ORDER BY indexed_at DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                results.extend([Verbete.from_row(row, c) for row in rows])
        
        return results

    def get_recent(self, court: Optional[str] = None, days: int = 30) -> List[Verbete]:
        """Obtém verbetes indexados recentemente."""
        results = []
        courts_to_search = [court] if court else ['STF', 'STJ']
        
        for c in courts_to_search:
            table_name = 'verbetes_stf' if c == 'STF' else 'verbetes_stj'
            
            with self._db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT * FROM {table_name}
                    WHERE indexed_at >= datetime('now', '-{days} days')
                    ORDER BY indexed_at DESC
                """)
                
                rows = cursor.fetchall()
                results.extend([Verbete.from_row(row, c) for row in rows])
        
        return results


# Instância singleton do repositório
verbetes_repository = VerbetesRepository()
