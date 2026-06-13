"""
Módulo de configuração e gerenciamento do banco de dados SQLite.

Este módulo centraliza a conexão com o banco de dados, inicialização do schema
e utilitários para migrações.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Gerenciador de conexões e schema do banco de dados SQLite.
    
    Implementa DatabaseProtocol — pode ser injetado via dependência
    em repositórios e serviços.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa o gerenciador de banco de dados.

        Args:
            db_path: Caminho para o arquivo do banco de dados. Se None, usa o padrão da config.
        """
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Usa o diretório data/db definido na estrutura
            base_dir = Path(__file__).parent.parent
            self.db_path = base_dir / "data" / "db" / "agente_juridico.db"
        
        # Garante que o diretório existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DatabaseManager initialized with path: {self.db_path}")

    @contextmanager
    def get_connection(self):
        """
        Context manager para obter uma conexão com o banco de dados.
        
        Yields:
            sqlite3.Connection: Conexão com o banco de dados.
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            conn.close()

    def initialize_schema(self):
        """
        Cria todas as tabelas necessárias se ainda não existirem.
        Deve ser chamado na inicialização da aplicação.
        """
        logger.info("Initializing database schema...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Habilita chaves estrangeiras
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            # Executa todos os scripts de criação de tabela
            self._create_customers_table(cursor)
            self._create_cases_table(cursor)
            self._create_case_states_table(cursor)
            self._create_documentos_table(cursor)
            self._create_verbetes_stf_table(cursor)
            self._create_verbetes_stj_table(cursor)
            self._create_fontes_url_table(cursor)
            self._create_knowledge_cache_table(cursor)
            self._create_auditlog_table(cursor)
            self._create_system_logs_table(cursor)
            
            # Cria índices para otimização
            self._create_indexes(cursor)
            
            # Cria views para consultas consolidadas
            self._create_views(cursor)
            
            # Cria triggers para auditoria automática
            self._create_triggers(cursor)
            
            logger.info("Database schema initialized successfully.")

    def _create_customers_table(self, cursor: sqlite3.Cursor):
        """Cria a tabela de clientes (pessoas físicas e jurídicas)."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL DEFAULT 'PF' CHECK(type IN ('PF', 'PJ')),
                name TEXT NOT NULL,
                document TEXT NOT NULL UNIQUE CHECK(length(document) IN (11, 14)),
                email TEXT,
                phone TEXT,
                address TEXT,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            );
        """)
        logger.debug("Table 'customers' created or verified.")

    def _create_cases_table(self, cursor: sqlite3.Cursor):
        """Cria a tabela de casos jurídicos."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                case_number TEXT NOT NULL,
                court TEXT NOT NULL,
                class TEXT,
                status TEXT DEFAULT 'ATIVO' CHECK(status IN ('ATIVO', 'SUSPENSO', 'ARQUIVADO', 'ENCERRADO')),
                subject TEXT,
                description TEXT,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
            );
        """)
        logger.debug("Table 'cases' created or verified.")

    def _create_case_states_table(self, cursor: sqlite3.Cursor):
        """Cria a tabela de estados da máquina de estados por caso."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                state_name TEXT NOT NULL,  -- e.g., 'initial', 'analysis', 'drafting'
                context_data JSON,  -- Snapshot do contexto atual
                transition_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
            );
        """)
        logger.debug("Table 'case_states' created or verified.")

    def _create_documentos_table(self, cursor: sqlite3.Cursor):
        """Cria a tabela de documentos e peças jurídicas."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                document_type TEXT NOT NULL,  -- e.g., 'peticao_inicial', 'contestacao'
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                is_latest BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                author_ai_model TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
            );
        """)
        logger.debug("Table 'documentos' created or verified.")

    def _create_verbetes_stf_table(self, cursor: sqlite3.Cursor):
        """Cria a tabela de verbetes e jurisprudência do STF."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verbetes_stf (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tema TEXT NOT NULL,
                resumo TEXT NOT NULL,
                keywords TEXT,  -- Lista de palavras-chave separadas por vírgula
                source_url TEXT,
                date_decision DATE,
                full_text TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        logger.debug("Table 'verbetes_stf' created or verified.")

    def _create_verbetes_stj_table(self, cursor: sqlite3.Cursor):
        """Cria a tabela de verbetes e jurisprudência do STJ."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verbetes_stj (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tema TEXT NOT NULL,
                resumo TEXT NOT NULL,
                keywords TEXT,
                source_url TEXT,
                date_decision DATE,
                full_text TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        logger.debug("Table 'verbetes_stj' created or verified.")

    def _create_fontes_url_table(self, cursor: sqlite3.Cursor):
        """Cria a tabela de fontes externas (URLs) utilizadas no RAG."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fontes_url (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                content_summary TEXT,
                content_hash TEXT NOT NULL,  -- Para detectar mudanças no conteúdo
                category TEXT,  -- e.g., 'legislacao', 'doutrina', 'jurisprudencia'
                last_scraped_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            );
        """)
        logger.debug("Table 'fontes_url' created or verified.")

    def _create_knowledge_cache_table(self, cursor: sqlite3.Cursor):
        """Cria a tabela de cache para vetores ou trechos de conhecimento processados."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,  -- 'verbete_stf', 'verbete_stj', 'url', 'local_file'
                source_id INTEGER,  -- ID na tabela de origem
                chunk_content TEXT NOT NULL,
                embedding BLOB,  -- Armazenamento binário do vetor (se necessário)
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        logger.debug("Table 'knowledge_cache' created or verified.")

    def _create_system_logs_table(self, cursor: sqlite3.Cursor):
        """Cria a tabela de logs de auditoria do sistema."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_level TEXT NOT NULL CHECK(log_level IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')),
                message TEXT NOT NULL,
                user_id TEXT,
                case_id INTEGER,
                action TEXT,
                details JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE SET NULL
            );
        """)
        logger.debug("Table 'system_logs' created or verified.")

    def _create_auditlog_table(self, cursor: sqlite3.Cursor):
        """Cria a tabela de auditoria de operações críticas."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditlog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL CHECK(table_name IN ('customers', 'cases', 'case_states', 'documentos', 'verbetes_stf', 'verbetes_stj', 'fontes_url', 'knowledge_cache')),
                operation TEXT NOT NULL CHECK(operation IN ('INSERT', 'UPDATE', 'DELETE')),
                record_id INTEGER NOT NULL,
                old_values JSON,
                new_values JSON,
                changed_by TEXT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                session_id TEXT,
                reason TEXT
            );
        """)
        logger.debug("Table 'auditlog' created or verified.")

    def _create_indexes(self, cursor: sqlite3.Cursor):
        """Cria índices para melhorar a performance das consultas."""
        indexes = [
            # Customers
            "CREATE INDEX IF NOT EXISTS idx_customers_document ON customers(document);",
            "CREATE INDEX IF NOT EXISTS idx_customers_type ON customers(type);",
            "CREATE INDEX IF NOT EXISTS idx_customers_active ON customers(is_active);",
            # Cases
            "CREATE INDEX IF NOT EXISTS idx_cases_customer ON cases(customer_id);",
            "CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);",
            "CREATE INDEX IF NOT EXISTS idx_cases_active ON cases(is_active);",
            # Case States
            "CREATE INDEX IF NOT EXISTS idx_case_states_case_id ON case_states(case_id);",
            # Documentos
            "CREATE INDEX IF NOT EXISTS idx_documentos_case_id ON documentos(case_id);",
            "CREATE INDEX IF NOT EXISTS idx_documentos_latest ON documentos(is_latest);",
            # Verbetes
            "CREATE INDEX IF NOT EXISTS idx_verbetes_stf_tema ON verbetes_stf(tema);",
            "CREATE INDEX IF NOT EXISTS idx_verbetes_stj_tema ON verbetes_stj(tema);",
            # Fontes URL
            "CREATE INDEX IF NOT EXISTS idx_fontes_url_hash ON fontes_url(content_hash);",
            # Knowledge Cache
            "CREATE INDEX IF NOT EXISTS idx_knowledge_cache_source ON knowledge_cache(source_type, source_id);",
            # System Logs
            "CREATE INDEX IF NOT EXISTS idx_system_logs_case ON system_logs(case_id);",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_date ON system_logs(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(log_level);",
            # Audit Log
            "CREATE INDEX IF NOT EXISTS idx_auditlog_table ON auditlog(table_name);",
            "CREATE INDEX IF NOT EXISTS idx_auditlog_operation ON auditlog(operation);",
            "CREATE INDEX IF NOT EXISTS idx_auditlog_record ON auditlog(record_id);",
            "CREATE INDEX IF NOT EXISTS idx_auditlog_changed_at ON auditlog(changed_at);",
            "CREATE INDEX IF NOT EXISTS idx_auditlog_table_record ON auditlog(table_name, record_id);",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        logger.debug("Database indexes created successfully.")

    def _create_views(self, cursor: sqlite3.Cursor):
        """Cria views para consultas consolidadas."""
        views = [
            # vw_customer_history: Histórico completo de casos por cliente
            """
            CREATE VIEW IF NOT EXISTS vw_customer_history AS
            SELECT
                c.id AS customer_id,
                c.name AS customer_name,
                c.type AS customer_type,
                c.document AS customer_document,
                cs.id AS case_id,
                cs.case_number,
                cs.court,
                cs.status AS case_status,
                cs.subject,
                cs.created_at AS case_created_at,
                COUNT(DISTINCT d.id) AS document_count,
                COUNT(DISTINCT cst.id) AS state_changes_count
            FROM customers c
            LEFT JOIN cases cs ON c.id = cs.customer_id AND cs.is_active = 1
            LEFT JOIN documentos d ON cs.id = d.case_id
            LEFT JOIN case_states cst ON cs.id = cst.case_id
            WHERE c.is_active = 1
            GROUP BY c.id, cs.id;
            """,
            # vw_audit_cases: Auditoria consolidada de operações em casos
            """
            CREATE VIEW IF NOT EXISTS vw_audit_cases AS
            SELECT
                a.id AS audit_id,
                a.table_name,
                a.operation,
                a.record_id AS case_id,
                json_extract(a.old_values, '$.case_number') AS old_case_number,
                json_extract(a.new_values, '$.case_number') AS new_case_number,
                json_extract(a.old_values, '$.status') AS old_status,
                json_extract(a.new_values, '$.status') AS new_status,
                a.changed_by,
                a.changed_at,
                a.reason
            FROM auditlog a
            WHERE a.table_name IN ('cases', 'case_states')
            ORDER BY a.changed_at DESC;
            """,
            # vw_recent_changes: Últimas alterações no sistema (últimas 24h)
            """
            CREATE VIEW IF NOT EXISTS vw_recent_changes AS
            SELECT
                a.table_name,
                a.operation,
                a.record_id,
                a.changed_by,
                a.changed_at,
                CASE a.table_name
                    WHEN 'customers' THEN 'Cliente'
                    WHEN 'cases' THEN 'Caso'
                    WHEN 'case_states' THEN 'Estado do Caso'
                    WHEN 'documentos' THEN 'Documento'
                    WHEN 'verbetes_stf' THEN 'Verbetes STF'
                    WHEN 'verbetes_stj' THEN 'Verbetes STJ'
                    WHEN 'fontes_url' THEN 'Fonte URL'
                    ELSE a.table_name
                END AS entity_type,
                CASE a.operation
                    WHEN 'INSERT' THEN 'Inserção'
                    WHEN 'UPDATE' THEN 'Atualização'
                    WHEN 'DELETE' THEN 'Exclusão'
                END AS operation_desc
            FROM auditlog a
            WHERE a.changed_at >= datetime('now', '-1 day')
            ORDER BY a.changed_at DESC
            LIMIT 100;
            """,
            # vw_case_timeline: Linha do tempo completa de um caso
            """
            CREATE VIEW IF NOT EXISTS vw_case_timeline AS
            SELECT
                cs.id AS case_id,
                cs.case_number,
                'CASE_CREATED' AS event_type,
                cs.created_at AS event_date,
                'Caso criado' AS description,
                NULL AS details
            FROM cases cs
            UNION ALL
            SELECT
                cst.case_id,
                cs.case_number,
                'STATE_CHANGE' AS event_type,
                cst.created_at AS event_date,
                'Mudança de estado: ' || cst.state_name AS description,
                cst.transition_reason AS details
            FROM case_states cst
            JOIN cases cs ON cst.case_id = cs.id
            UNION ALL
            SELECT
                d.case_id,
                cs.case_number,
                'DOCUMENT_CREATED' AS event_type,
                d.created_at AS event_date,
                'Documento criado: ' || d.title AS description,
                json_object('version', d.version, 'type', d.document_type) AS details
            FROM documentos d
            JOIN cases cs ON d.case_id = cs.id
            ORDER BY event_date DESC;
            """,
            # vw_knowledge_stats: Estatísticas de conhecimento
            """
            CREATE VIEW IF NOT EXISTS vw_knowledge_stats AS
            SELECT
                'STF' AS source,
                COUNT(*) AS total_records,
                MAX(indexed_at) AS last_updated
            FROM verbetes_stf
            UNION ALL
            SELECT
                'STJ' AS source,
                COUNT(*) AS total_records,
                MAX(indexed_at) AS last_updated
            FROM verbetes_stj
            UNION ALL
            SELECT
                'URLs Ativas' AS source,
                COUNT(*) AS total_records,
                MAX(last_scraped_at) AS last_updated
            FROM fontes_url
            WHERE is_active = 1;
            """,
        ]
        
        for view_sql in views:
            cursor.execute(view_sql)
        
        logger.debug("Database views created successfully.")

    def _create_triggers(self, cursor: sqlite3.Cursor):
        """Cria triggers para auditoria automática e manutenção."""
        triggers = [
            # Trigger: Atualizar updated_at em customers
            """
            CREATE TRIGGER IF NOT EXISTS trg_customers_updated_at
            AFTER UPDATE ON customers
            BEGIN
                UPDATE customers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """,
            # Trigger: Atualizar updated_at em cases
            """
            CREATE TRIGGER IF NOT EXISTS trg_cases_updated_at
            AFTER UPDATE ON cases
            BEGIN
                UPDATE cases SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """,
            # Trigger: Auditoria INSERT em customers
            """
            CREATE TRIGGER IF NOT EXISTS trg_audit_customers_insert
            AFTER INSERT ON customers
            BEGIN
                INSERT INTO auditlog (table_name, operation, record_id, new_values, changed_at)
                VALUES ('customers', 'INSERT', NEW.id, json_object('id', NEW.id, 'name', NEW.name, 'document', NEW.document), CURRENT_TIMESTAMP);
            END;
            """,
            # Trigger: Auditoria UPDATE em customers
            """
            CREATE TRIGGER IF NOT EXISTS trg_audit_customers_update
            AFTER UPDATE ON customers
            BEGIN
                INSERT INTO auditlog (table_name, operation, record_id, old_values, new_values, changed_at)
                VALUES ('customers', 'UPDATE', NEW.id, 
                        json_object('id', OLD.id, 'name', OLD.name, 'document', OLD.document),
                        json_object('id', NEW.id, 'name', NEW.name, 'document', NEW.document),
                        CURRENT_TIMESTAMP);
            END;
            """,
            # Trigger: Auditoria DELETE em customers
            """
            CREATE TRIGGER IF NOT EXISTS trg_audit_customers_delete
            AFTER DELETE ON customers
            BEGIN
                INSERT INTO auditlog (table_name, operation, record_id, old_values, changed_at)
                VALUES ('customers', 'DELETE', OLD.id, json_object('id', OLD.id, 'name', OLD.name, 'document', OLD.document), CURRENT_TIMESTAMP);
            END;
            """,
            # Trigger: Auditoria INSERT em cases
            """
            CREATE TRIGGER IF NOT EXISTS trg_audit_cases_insert
            AFTER INSERT ON cases
            BEGIN
                INSERT INTO auditlog (table_name, operation, record_id, new_values, changed_at)
                VALUES ('cases', 'INSERT', NEW.id, json_object('id', NEW.id, 'case_number', NEW.case_number, 'customer_id', NEW.customer_id), CURRENT_TIMESTAMP);
            END;
            """,
            # Trigger: Auditoria UPDATE em cases
            """
            CREATE TRIGGER IF NOT EXISTS trg_audit_cases_update
            AFTER UPDATE ON cases
            BEGIN
                INSERT INTO auditlog (table_name, operation, record_id, old_values, new_values, changed_at)
                VALUES ('cases', 'UPDATE', NEW.id,
                        json_object('id', OLD.id, 'case_number', OLD.case_number, 'status', OLD.status),
                        json_object('id', NEW.id, 'case_number', NEW.case_number, 'status', NEW.status),
                        CURRENT_TIMESTAMP);
            END;
            """,
            # Trigger: Invalidar versões anteriores de documentos quando novo é criado
            """
            CREATE TRIGGER IF NOT EXISTS trg_documentos_invalidate_old
            AFTER INSERT ON documentos
            WHEN NEW.is_latest = 1
            BEGIN
                UPDATE documentos SET is_latest = 0
                WHERE case_id = NEW.case_id 
                  AND document_type = NEW.document_type 
                  AND id != NEW.id;
            END;
            """,
        ]
        
        for trigger_sql in triggers:
            cursor.execute(trigger_sql)
        
        logger.debug("Database triggers created successfully.")


# Instância singleton para uso global
db_manager = DatabaseManager()


def init_db():
    """Função utilitária para inicializar o banco de dados."""
    db_manager.initialize_schema()


if __name__ == "__main__":
    # Script para inicializar o DB manualmente se necessário
    init_db()
    print(f"Database initialized at: {db_manager.db_path}")
