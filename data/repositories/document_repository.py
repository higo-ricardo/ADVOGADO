"""
Repositório para gerenciamento de Documentos e Peças Jurídicas.

Este módulo fornece operações CRUD para a tabela 'documentos',
incluindo controle de versionamento.
"""

import json
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime

from data.database import db_manager
from infrastructure.logging_config import get_logger

logger = get_logger(__name__)


class Document:
    """Modelo de dados para um Documento Jurídico."""
    
    def __init__(self, id: int, case_id: int, document_type: str, 
                 title: str, content: str, version: int = 1,
                 is_latest: bool = True, created_at: Optional[datetime] = None,
                 author_ai_model: Optional[str] = None):
        self.id = id
        self.case_id = case_id
        self.document_type = document_type
        self.title = title
        self.content = content
        self.version = version
        self.is_latest = is_latest
        self.created_at = created_at
        self.author_ai_model = author_ai_model

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Document':
        """Cria uma instância de Document a partir de uma linha do banco de dados."""
        return cls(
            id=row['id'],
            case_id=row['case_id'],
            document_type=row['document_type'],
            title=row['title'],
            content=row['content'],
            version=row['version'],
            is_latest=bool(row['is_latest']),
            created_at=row['created_at'],
            author_ai_model=row['author_ai_model']
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto Document para um dicionário."""
        return {
            'id': self.id,
            'case_id': self.case_id,
            'document_type': self.document_type,
            'title': self.title,
            'content': self.content,
            'version': self.version,
            'is_latest': self.is_latest,
            'created_at': str(self.created_at) if self.created_at else None,
            'author_ai_model': self.author_ai_model
        }


class DocumentRepository:
    """Repositório para operações com documentos jurídicos."""

    def create(self, case_id: int, document_type: str, title: str, 
               content: str, author_ai_model: Optional[str] = None) -> Document:
        """
        Cria um novo documento.
        
        Automaticamente marca versões anteriores do mesmo tipo como não-latest.
        
        Returns:
            Document: O objeto Document criado.
        """
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Marca versões anteriores como não-latest
            cursor.execute("""
                UPDATE documentos 
                SET is_latest = 0 
                WHERE case_id = ? AND document_type = ?
            """, (case_id, document_type))
            
            # Determina o próximo número de versão
            cursor.execute("""
                SELECT MAX(version) FROM documentos 
                WHERE case_id = ? AND document_type = ?
            """, (case_id, document_type))
            result = cursor.fetchone()
            next_version = (result[0] or 0) + 1
            
            # Insere o novo documento
            cursor.execute("""
                INSERT INTO documentos (case_id, document_type, title, content, version, author_ai_model)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (case_id, document_type, title, content, next_version, author_ai_model))
            
            doc_id = cursor.lastrowid
        
        # Log da ação (fora da transação principal para evitar lock)
        self._log_action(case_id, 'CREATE_DOCUMENT', {
            'doc_id': doc_id,
            'type': document_type,
            'version': next_version
        })
        
        return self.get_by_id(doc_id)

    def get_by_id(self, doc_id: int) -> Optional[Document]:
        """Obtém um documento pelo ID."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documentos WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            return Document.from_row(row) if row else None

    def get_by_case(self, case_id: int, 
                    document_type: Optional[str] = None,
                    latest_only: bool = False) -> List[Document]:
        """
        Obtém documentos de um caso.
        
        Args:
            case_id: ID do caso.
            document_type: Filtra por tipo específico (opcional).
            latest_only: Se True, retorna apenas a versão mais recente de cada tipo.
        """
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM documentos WHERE case_id = ?"
            params = [case_id]
            
            if document_type:
                query += " AND document_type = ?"
                params.append(document_type)
            
            if latest_only:
                query += " AND is_latest = 1"
            
            query += " ORDER BY document_type, version DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [Document.from_row(row) for row in rows]

    def get_latest_version(self, case_id: int, document_type: str) -> Optional[Document]:
        """Obtém a versão mais recente de um tipo de documento em um caso."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM documentos 
                WHERE case_id = ? AND document_type = ? AND is_latest = 1
            """, (case_id, document_type))
            row = cursor.fetchone()
            return Document.from_row(row) if row else None

    def update_content(self, doc_id: int, new_content: str, 
                       author_ai_model: Optional[str] = None) -> Document:
        """
        Atualiza o conteúdo de um documento, criando uma nova versão.
        
        Na verdade, isso cria um NOVO documento com versão incrementada,
        mantendo o histórico intacto.
        """
        doc = self.get_by_id(doc_id)
        if not doc:
            raise ValueError(f"Document with id {doc_id} not found")
        
        # Cria nova versão
        return self.create(
            case_id=doc.case_id,
            document_type=doc.document_type,
            title=doc.title,  # Mantém o mesmo título ou poderia adicionar sufixo
            content=new_content,
            author_ai_model=author_ai_model
        )

    def delete(self, doc_id: int) -> bool:
        """Exclui um documento específico."""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documentos WHERE id = ?", (doc_id,))
            
            if cursor.rowcount > 0:
                self._log_action(None, 'DELETE_DOCUMENT', {'doc_id': doc_id})
                return True
            return False

    def _log_action(self, case_id: Optional[int], action: str, details: Dict[str, Any]):
        """Registra uma ação nos logs do sistema."""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO system_logs (log_level, message, case_id, action, details)
                    VALUES (?, ?, ?, ?, ?)
                """, ('INFO', f'Action {action} performed', 
                      case_id, action, json.dumps(details)))
        except Exception as e:
            logger.error(f"Failed to log action: {e}")


# Instância singleton do repositório
document_repository = DocumentRepository()
