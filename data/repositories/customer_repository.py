"""
Customer Repository - Repositório para gestão de clientes.
"""
import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

import logging
logger = logging.getLogger(__name__)


class CustomerRepository:
    """Repositório para operações CRUD de clientes."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa o repositório de clientes.

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
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def create(self, name: str, document: str, customer_type: str = 'PF',
               email: Optional[str] = None, phone: Optional[str] = None,
               address: Optional[str] = None, metadata: Optional[Dict] = None) -> int:
        """
        Cria um novo cliente.

        Args:
            name: Nome completo ou razão social
            document: CPF ou CNPJ (apenas números)
            customer_type: 'PF' ou 'PJ'
            email: E-mail para contato
            phone: Telefone/celular
            address: Endereço completo
            metadata: Dados adicionais em JSON

        Returns:
            int: ID do cliente criado

        Raises:
            sqlite3.IntegrityError: Se documento já existir
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO customers (type, name, document, email, phone, address, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (customer_type, name, document, email, phone, address, metadata_json))
            
            conn.commit()
            customer_id = cursor.lastrowid
            logger.info(f"Customer created: id={customer_id}, name={name}, document={document}")
            return customer_id
            
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to create customer: {e}")
            raise
        finally:
            conn.close()

    def get_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um cliente por ID.

        Args:
            customer_id: ID do cliente

        Returns:
            Dict com dados do cliente ou None se não encontrado
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            
            if row:
                customer = dict(row)
                if customer.get('metadata'):
                    customer['metadata'] = json.loads(customer['metadata'])
                return customer
            return None
        finally:
            conn.close()

    def get_by_document(self, document: str) -> Optional[Dict[str, Any]]:
        """
        Obtém um cliente por documento (CPF/CNPJ).

        Args:
            document: CPF ou CNPJ

        Returns:
            Dict com dados do cliente ou None se não encontrado
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE document = ?", (document,))
            row = cursor.fetchone()
            
            if row:
                customer = dict(row)
                if customer.get('metadata'):
                    customer['metadata'] = json.loads(customer['metadata'])
                return customer
            return None
        finally:
            conn.close()

    def list_all(self, active_only: bool = True, customer_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista todos os clientes.

        Args:
            active_only: Se True, retorna apenas clientes ativos
            customer_type: Filtra por tipo ('PF' ou 'PJ')

        Returns:
            Lista de dicionários com dados dos clientes
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            query = "SELECT * FROM customers WHERE 1=1"
            params = []
            
            if active_only:
                query += " AND is_active = 1"
            
            if customer_type:
                query += " AND type = ?"
                params.append(customer_type)
            
            query += " ORDER BY name"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            customers = []
            for row in rows:
                customer = dict(row)
                if customer.get('metadata'):
                    customer['metadata'] = json.loads(customer['metadata'])
                customers.append(customer)
            
            return customers
        finally:
            conn.close()

    def update(self, customer_id: int, name: Optional[str] = None,
               email: Optional[str] = None, phone: Optional[str] = None,
               address: Optional[str] = None, metadata: Optional[Dict] = None,
               is_active: Optional[bool] = None,
               changed_by: Optional[str] = None) -> bool:
        """
        Atualiza dados de um cliente.

        Args:
            customer_id: ID do cliente
            name: Novo nome (opcional)
            email: Novo e-mail (opcional)
            phone: Novo telefone (opcional)
            address: Novo endereço (opcional)
            metadata: Novos metadados (opcional)
            is_active: Novo status (opcional)
            changed_by: Usuário responsável pela atualização

        Returns:
            bool: True se atualizado com sucesso
        """
        conn = self._get_connection()
        try:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if email is not None:
                updates.append("email = ?")
                params.append(email)
            if phone is not None:
                updates.append("phone = ?")
                params.append(phone)
            if address is not None:
                updates.append("address = ?")
                params.append(address)
            if metadata is not None:
                updates.append("metadata = ?")
                params.append(json.dumps(metadata))
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)
            
            if not updates:
                return False
            
            params.append(customer_id)
            
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE customers SET {', '.join(updates)} WHERE id = ?
            """, params)
            
            conn.commit()
            updated = cursor.rowcount > 0
            if updated:
                logger.info(f"Customer updated: id={customer_id}")
            return updated
        finally:
            conn.close()

    def delete(self, customer_id: int, soft_delete: bool = True) -> bool:
        """
        Remove um cliente.

        Args:
            customer_id: ID do cliente
            soft_delete: Se True, apenas desativa o cliente

        Returns:
            bool: True se removido/desativado com sucesso
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            if soft_delete:
                cursor.execute("""
                    UPDATE customers SET is_active = 0 WHERE id = ?
                """, (customer_id,))
            else:
                cursor.execute("""
                    DELETE FROM customers WHERE id = ?
                """, (customer_id,))
            
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Customer {'deactivated' if soft_delete else 'deleted'}: id={customer_id}")
            return deleted
        finally:
            conn.close()

    def search(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Busca clientes por nome ou documento.

        Args:
            search_term: Termo de busca

        Returns:
            Lista de clientes encontrados
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            search_pattern = f"%{search_term}%"
            
            cursor.execute("""
                SELECT * FROM customers 
                WHERE (name LIKE ? OR document LIKE ?) AND is_active = 1
                ORDER BY name
            """, (search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            customers = []
            for row in rows:
                customer = dict(row)
                if customer.get('metadata'):
                    customer['metadata'] = json.loads(customer['metadata'])
                customers.append(customer)
            
            return customers
        finally:
            conn.close()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de clientes.

        Returns:
            Dict com estatísticas
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total de clientes
            cursor.execute("SELECT COUNT(*) as total FROM customers WHERE is_active = 1")
            stats['total_active'] = cursor.fetchone()['total']
            
            # Por tipo
            cursor.execute("""
                SELECT type, COUNT(*) as count 
                FROM customers 
                WHERE is_active = 1 
                GROUP BY type
            """)
            stats['by_type'] = {row['type']: row['count'] for row in cursor.fetchall()}
            
            return stats
        finally:
            conn.close()
