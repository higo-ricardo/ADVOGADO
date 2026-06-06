"""
AuditLog Repository - Repositório para gestão de logs de auditoria.
"""
import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

import logging
logger = logging.getLogger(__name__)


class AuditLogRepository:
    """Repositório para operações de auditoria."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa o repositório de auditoria.

        Args:
            db_path: Caminho para o banco de dados. Se None, usa o padrão.
        """
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Caminho absoluto correto: /workspace/data/db/agente_juridico.db
            self.db_path = Path(__file__).parent.parent / "db" / "agente_juridico.db"
        
        # Garante que o arquivo existe
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Obtém uma conexão com o banco de dados."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def log_operation(self, table_name: str, operation: str, record_id: int,
                      old_values: Optional[Dict] = None,
                      new_values: Optional[Dict] = None,
                      changed_by: Optional[str] = None,
                      ip_address: Optional[str] = None,
                      session_id: Optional[str] = None,
                      reason: Optional[str] = None) -> int:
        """
        Registra uma operação de auditoria.

        Args:
            table_name: Nome da tabela afetada
            operation: Operação realizada ('INSERT', 'UPDATE', 'DELETE')
            record_id: ID do registro afetado
            old_values: Valores anteriores (para UPDATE/DELETE)
            new_values: Novos valores (para INSERT/UPDATE)
            changed_by: Usuário responsável
            ip_address: IP de origem
            session_id: Sessão da operação
            reason: Justificativa da operação

        Returns:
            int: ID do registro de auditoria criado
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            old_values_json = json.dumps(old_values) if old_values else None
            new_values_json = json.dumps(new_values) if new_values else None
            
            cursor.execute("""
                INSERT INTO auditlog 
                (table_name, operation, record_id, old_values, new_values, 
                 changed_by, ip_address, session_id, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (table_name, operation, record_id, old_values_json, 
                  new_values_json, changed_by, ip_address, session_id, reason))
            
            conn.commit()
            audit_id = cursor.lastrowid
            logger.debug(f"Audit log created: id={audit_id}, table={table_name}, op={operation}")
            return audit_id
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            raise
        finally:
            conn.close()

    def get_by_id(self, audit_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um registro de auditoria por ID.

        Args:
            audit_id: ID do registro

        Returns:
            Dict com dados do registro ou None
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM auditlog WHERE id = ?", (audit_id,))
            row = cursor.fetchone()
            
            if row:
                audit = dict(row)
                if audit.get('old_values'):
                    audit['old_values'] = json.loads(audit['old_values'])
                if audit.get('new_values'):
                    audit['new_values'] = json.loads(audit['new_values'])
                return audit
            return None
        finally:
            conn.close()

    def get_by_table(self, table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtém registros de auditoria por tabela.

        Args:
            table_name: Nome da tabela
            limit: Limite de registros

        Returns:
            Lista de registros de auditoria
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM auditlog 
                WHERE table_name = ? 
                ORDER BY changed_at DESC 
                LIMIT ?
            """, (table_name, limit))
            
            rows = cursor.fetchall()
            audits = []
            for row in rows:
                audit = dict(row)
                if audit.get('old_values'):
                    audit['old_values'] = json.loads(audit['old_values'])
                if audit.get('new_values'):
                    audit['new_values'] = json.loads(audit['new_values'])
                audits.append(audit)
            
            return audits
        finally:
            conn.close()

    def get_by_record(self, table_name: str, record_id: int) -> List[Dict[str, Any]]:
        """
        Obtém histórico de auditoria de um registro específico.

        Args:
            table_name: Nome da tabela
            record_id: ID do registro

        Returns:
            Lista de registros de auditoria ordenados por data
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM auditlog 
                WHERE table_name = ? AND record_id = ? 
                ORDER BY changed_at ASC
            """, (table_name, record_id))
            
            rows = cursor.fetchall()
            audits = []
            for row in rows:
                audit = dict(row)
                if audit.get('old_values'):
                    audit['old_values'] = json.loads(audit['old_values'])
                if audit.get('new_values'):
                    audit['new_values'] = json.loads(audit['new_values'])
                audits.append(audit)
            
            return audits
        finally:
            conn.close()

    def get_by_user(self, changed_by: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Obtém registros de auditoria por usuário.

        Args:
            changed_by: Nome do usuário
            days: Número de dias para retroceder

        Returns:
            Lista de registros de auditoria
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            since_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                SELECT * FROM auditlog 
                WHERE changed_by = ? AND changed_at >= ?
                ORDER BY changed_at DESC
            """, (changed_by, since_date.isoformat()))
            
            rows = cursor.fetchall()
            audits = []
            for row in rows:
                audit = dict(row)
                if audit.get('old_values'):
                    audit['old_values'] = json.loads(audit['old_values'])
                if audit.get('new_values'):
                    audit['new_values'] = json.loads(audit['new_values'])
                audits.append(audit)
            
            return audits
        finally:
            conn.close()

    def get_recent_changes(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Obtém mudanças recentes no sistema.

        Args:
            hours: Número de horas para retroceder

        Returns:
            Lista de registros de auditoria recentes
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            since_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute("""
                SELECT * FROM auditlog 
                WHERE changed_at >= ?
                ORDER BY changed_at DESC
                LIMIT 100
            """, (since_time.isoformat(),))
            
            rows = cursor.fetchall()
            audits = []
            for row in rows:
                audit = dict(row)
                if audit.get('old_values'):
                    audit['old_values'] = json.loads(audit['old_values'])
                if audit.get('new_values'):
                    audit['new_values'] = json.loads(audit['new_values'])
                audits.append(audit)
            
            return audits
        finally:
            conn.close()

    def get_by_operation(self, operation: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtém registros de auditoria por tipo de operação.

        Args:
            operation: Tipo de operação ('INSERT', 'UPDATE', 'DELETE')
            limit: Limite de registros

        Returns:
            Lista de registros de auditoria
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM auditlog 
                WHERE operation = ? 
                ORDER BY changed_at DESC 
                LIMIT ?
            """, (operation, limit))
            
            rows = cursor.fetchall()
            audits = []
            for row in rows:
                audit = dict(row)
                if audit.get('old_values'):
                    audit['old_values'] = json.loads(audit['old_values'])
                if audit.get('new_values'):
                    audit['new_values'] = json.loads(audit['new_values'])
                audits.append(audit)
            
            return audits
        finally:
            conn.close()

    def search(self, table_name: Optional[str] = None,
               operation: Optional[str] = None,
               changed_by: Optional[str] = None,
               since_date: Optional[datetime] = None,
               until_date: Optional[datetime] = None,
               limit: int = 100) -> List[Dict[str, Any]]:
        """
        Busca avançada em registros de auditoria.

        Args:
            table_name: Filtra por tabela
            operation: Filtra por operação
            changed_by: Filtra por usuário
            since_date: Data inicial
            until_date: Data final
            limit: Limite de registros

        Returns:
            Lista de registros de auditoria
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            query = "SELECT * FROM auditlog WHERE 1=1"
            params = []
            
            if table_name:
                query += " AND table_name = ?"
                params.append(table_name)
            
            if operation:
                query += " AND operation = ?"
                params.append(operation)
            
            if changed_by:
                query += " AND changed_by = ?"
                params.append(changed_by)
            
            if since_date:
                query += " AND changed_at >= ?"
                params.append(since_date.isoformat())
            
            if until_date:
                query += " AND changed_at <= ?"
                params.append(until_date.isoformat())
            
            query += " ORDER BY changed_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            rows = cursor.fetchall()
            audits = []
            for row in rows:
                audit = dict(row)
                if audit.get('old_values'):
                    audit['old_values'] = json.loads(audit['old_values'])
                if audit.get('new_values'):
                    audit['new_values'] = json.loads(audit['new_values'])
                audits.append(audit)
            
            return audits
        finally:
            conn.close()

    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtém estatísticas de auditoria.

        Args:
            days: Número de dias para análise

        Returns:
            Dict com estatísticas
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            since_date = datetime.now() - timedelta(days=days)
            
            stats = {}
            
            # Total de operações
            cursor.execute("""
                SELECT COUNT(*) as total FROM auditlog 
                WHERE changed_at >= ?
            """, (since_date.isoformat(),))
            stats['total_operations'] = cursor.fetchone()['total']
            
            # Por operação
            cursor.execute("""
                SELECT operation, COUNT(*) as count 
                FROM auditlog 
                WHERE changed_at >= ?
                GROUP BY operation
            """, (since_date.isoformat(),))
            stats['by_operation'] = {row['operation']: row['count'] for row in cursor.fetchall()}
            
            # Por tabela
            cursor.execute("""
                SELECT table_name, COUNT(*) as count 
                FROM auditlog 
                WHERE changed_at >= ?
                GROUP BY table_name
                ORDER BY count DESC
            """, (since_date.isoformat(),))
            stats['by_table'] = {row['table_name']: row['count'] for row in cursor.fetchall()}
            
            # Top usuários
            cursor.execute("""
                SELECT changed_by, COUNT(*) as count 
                FROM auditlog 
                WHERE changed_at >= ? AND changed_by IS NOT NULL
                GROUP BY changed_by
                ORDER BY count DESC
                LIMIT 10
            """, (since_date.isoformat(),))
            stats['top_users'] = {row['changed_by']: row['count'] for row in cursor.fetchall()}
            
            return stats
        finally:
            conn.close()

    def cleanup_old_records(self, days: int = 365) -> int:
        """
        Remove registros de auditoria antigos.

        Args:
            days: Manter registros dos últimos N dias

        Returns:
            int: Número de registros removidos
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                DELETE FROM auditlog 
                WHERE changed_at < ?
            """, (cutoff_date.isoformat(),))
            
            conn.commit()
            deleted = cursor.rowcount
            logger.info(f"Cleaned up {deleted} old audit log records")
            return deleted
        finally:
            conn.close()
