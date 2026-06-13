"""
Repositório para gerenciamento de Casos Jurídicos.

Este módulo fornece operações CRUD e consultas específicas para a tabela 'cases'.
"""

import json
import sqlite3
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

from infrastructure.logging_config import get_logger

if TYPE_CHECKING:
    from src.domain.interfaces import DatabaseProtocol

logger = get_logger(__name__)


class Case:
    """Modelo de dados para um Caso Jurídico."""
    
    def __init__(self, id: int, client_name: str, case_type: str, 
                 description: Optional[str] = None, status: str = 'active',
                 created_at: Optional[datetime] = None, 
                 updated_at: Optional[datetime] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.id = id
        self.client_name = client_name
        self.case_type = case_type
        self.description = description
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.metadata = metadata or {}

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Case':
        """Cria uma instância de Case a partir de uma linha do banco de dados."""
        metadata = json.loads(row['metadata']) if row['metadata'] else None
        return cls(
            id=row['id'],
            client_name=row['client_name'],
            case_type=row['case_type'],
            description=row['description'],
            status=row['status'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            metadata=metadata
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto Case para um dicionário."""
        return {
            'id': self.id,
            'client_name': self.client_name,
            'case_type': self.case_type,
            'description': self.description,
            'status': self.status,
            'created_at': str(self.created_at) if self.created_at else None,
            'updated_at': str(self.updated_at) if self.updated_at else None,
            'metadata': self.metadata
        }


class CaseRepository:
    """Repositório para operações com casos jurídicos."""

    def __init__(self, db: "DatabaseProtocol | None" = None):
        """
        Inicializa o repositório.
        
        Args:
            db: Instância de DatabaseProtocol. Se None, usa o singleton global.
        """
        if db is not None:
            self._db = db
        else:
            from data.database import db_manager
            self._db = db_manager

    def create(self, client_name: str, case_type: str, 
               description: Optional[str] = None, 
               metadata: Optional[Dict[str, Any]] = None) -> Case:
        """
        Cria um novo caso jurídico.
        
        Returns:
            Case: O objeto Case criado com ID preenchido.
        """
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO cases (client_name, case_type, description, metadata)
                VALUES (?, ?, ?, ?)
            """, (client_name, case_type, description, metadata_json))
            
            case_id = cursor.lastrowid
        
        # Log da ação (fora da transação principal para evitar lock)
        self._log_action(case_id, 'CREATE_CASE', {'client_name': client_name})
        
        # Busca o caso criado para retornar o objeto completo
        return self.get_by_id(case_id)

    def get_by_id(self, case_id: int) -> Optional[Case]:
        """Obtém um caso pelo ID."""
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
            row = cursor.fetchone()
            return Case.from_row(row) if row else None

    def get_all(self, status: Optional[str] = None, 
                case_type: Optional[str] = None) -> List[Case]:
        """
        Obtém todos os casos, opcionalmente filtrados por status ou tipo.
        """
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM cases WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            if case_type:
                query += " AND case_type = ?"
                params.append(case_type)
                
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [Case.from_row(row) for row in rows]

    def update_status(self, case_id: int, new_status: str) -> bool:
        """Atualiza o status de um caso."""
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cases 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_status, case_id))
            
            if cursor.rowcount > 0:
                self._log_action(case_id, 'UPDATE_STATUS', {'new_status': new_status})
                return True
            return False

    def update_metadata(self, case_id: int, metadata: Dict[str, Any]) -> bool:
        """Atualiza os metadados de um caso."""
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            metadata_json = json.dumps(metadata)
            
            cursor.execute("""
                UPDATE cases 
                SET metadata = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (metadata_json, case_id))
            
            return cursor.rowcount > 0

    def delete(self, case_id: int) -> bool:
        """Exclui um caso (e seus estados/documentos relacionados via CASCADE)."""
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cases WHERE id = ?", (case_id,))
            
            if cursor.rowcount > 0:
                self._log_action(case_id, 'DELETE_CASE', {})
                return True
            return False

    def _log_action(self, case_id: int, action: str, details: Dict[str, Any]):
        """Registra uma ação nos logs do sistema."""
        try:
            with self._db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO system_logs (log_level, message, case_id, action, details)
                    VALUES (?, ?, ?, ?, ?)
                """, ('INFO', f'Action {action} performed on case {case_id}', 
                      case_id, action, json.dumps(details)))
        except Exception as e:
            logger.error(f"Failed to log action: {e}")


# Instância singleton do repositório
case_repository = CaseRepository()
