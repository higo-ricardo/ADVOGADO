# Guia de Estruturação do Banco de Dados
## Agente Jurídico IA - SQLite

---

## 1. Visão Geral

Este documento descreve a estrutura completa do banco de dados SQLite utilizado no sistema Agente Jurídico IA, incluindo tabelas, relacionamentos, constraints, índices, views, triggers e padrões de uso.

### 1.1 Objetivos
- Persistência confiável de casos jurídicos e documentos
- Gestão especializada de jurisprudências STF e STJ
- Rastreabilidade completa através de audit log
- Suporte a operações RAG (Retrieval-Augmented Generation)
- Conformidade com LGPD e requisitos de auditoria

### 1.2 Tecnologias
- **SGBD**: SQLite >= 3.35.0
- **Linguagem**: Python 3.10+
- **Bibliotecas**: aiosqlite, python-dateutil
- **Modo**: WAL (Write-Ahead Logging)

---

## 2. Schema do Banco de Dados

### 2.1 Diagrama Entidade-Relacionamento

```
┌─────────────┐       ┌─────────────┐       ┌──────────────┐
│  customers  │───┬──▶│    cases    │───┬──▶│ case_states  │
└─────────────┘   │   └─────────────┘   │   └──────────────┘
                  │                     │
                  │                     ├──▶│  documentos   │
                  │                     │   └──────────────┘
                  │                     │
                  │                     │
┌─────────────┐   │   ┌───────────────┐ │   ┌──────────────┐
│ fontes_url  │───┼──▶│ verbetes_stf  │ │   │ knowledge_   │
└─────────────┘   │   └───────────────┘ │   │    cache     │
                  │                     │   └──────────────┘
                  │   ┌───────────────┐ │
                  └──▶│ verbetes_stj  │ │
                      └───────────────┘ │
                                        │
┌─────────────┐                         │
│  auditlog   │◀────────────────────────┘
└─────────────┘
┌─────────────┐
│system_logs  │
└─────────────┘
```

---

## 3. Tabelas

### 3.1 `customers`

**Descrição**: Armazena informações de clientes (pessoas físicas e jurídicas).

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| id | INTEGER | NO | AUTOINCREMENT | Chave primária |
| type | TEXT | NO | 'PF' | Tipo: PF (Pessoa Física) ou PJ (Pessoa Jurídica) |
| name | TEXT | NO | - | Nome completo ou razão social |
| document | TEXT | NO | - | CPF ou CNPJ (apenas números) |
| email | TEXT | YES | NULL | E-mail para contato |
| phone | TEXT | YES | NULL | Telefone/celular |
| address | TEXT | YES | NULL | Endereço completo |
| metadata | TEXT | YES | NULL | JSON com dados adicionais |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de criação |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de atualização |
| is_active | BOOLEAN | NO | TRUE | Status do cadastro |

**Constraints**:
- PRIMARY KEY: `id`
- UNIQUE: `document` (UK_customers_document)
- CHECK: `type IN ('PF', 'PJ')`
- CHECK: `length(document) IN (11, 14)` (CPF=11, CNPJ=14)

**Índices**:
- `idx_customers_document`: Busca por documento
- `idx_customers_type`: Filtragem por tipo
- `idx_customers_active`: Filtragem por status

---

### 3.2 `cases`

**Descrição**: Registro de casos jurídicos vinculados a clientes.

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| id | INTEGER | NO | AUTOINCREMENT | Chave primária |
| customer_id | INTEGER | NO | - | FK para customers |
| case_number | TEXT | NO | - | Número do processo |
| court | TEXT | NO | - | Tribunal/Vara |
| class | TEXT | YES | NULL | Classe processual |
| status | TEXT | NO | 'ATIVO' | Status do caso |
| subject | TEXT | YES | NULL | Assunto principal |
| description | TEXT | YES | NULL | Descrição detalhada |
| metadata | TEXT | YES | NULL | JSON com dados adicionais |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de criação |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de atualização |
| is_active | BOOLEAN | NO | TRUE | Status do caso |

**Constraints**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `customer_id` REFERENCES customers(id) ON DELETE CASCADE
- UNIQUE: `case_number` (UK_cases_number)
- CHECK: `status IN ('ATIVO', 'SUSPENSO', 'ARQUIVADO', 'ENCERRADO')`

**Índices**:
- `idx_cases_customer_id`: Casos por cliente
- `idx_cases_number`: Busca por número processual
- `idx_cases_status`: Filtragem por status
- `idx_cases_court`: Agrupamento por tribunal
- `idx_cases_customer_status`: Índice composto (customer_id, status)

---

### 3.3 `case_states`

**Descrição**: Histórico versionado de mudanças de estado dos casos.

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| id | INTEGER | NO | AUTOINCREMENT | Chave primária |
| case_id | INTEGER | NO | - | FK para cases |
| status | TEXT | NO | - | Novo status |
| previous_status | TEXT | YES | NULL | Status anterior |
| description | TEXT | YES | NULL | Descrição da mudança |
| reason | TEXT | YES | NULL | Motivo da alteração |
| changed_by | TEXT | YES | NULL | Usuário responsável |
| changed_at | DATETIME | NO | CURRENT_TIMESTAMP | Data da mudança |
| metadata | TEXT | YES | NULL | JSON com contexto adicional |

**Constraints**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `case_id` REFERENCES cases(id) ON DELETE CASCADE
- CHECK: `status IN ('ATIVO', 'SUSPENSO', 'ARQUIVADO', 'ENCERRADO')`

**Índices**:
- `idx_case_states_case_id`: Histórico por caso
- `idx_case_states_changed_at`: Ordenação temporal
- `idx_case_states_user`: Auditoria por usuário

---

### 3.4 `documentos`

**Descrição**: Armazenamento de documentos processuais com versionamento.

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| id | INTEGER | NO | AUTOINCREMENT | Chave primária |
| case_id | INTEGER | NO | - | FK para cases |
| version | INTEGER | NO | 1 | Versão do documento |
| doc_type | TEXT | NO | - | Tipo: PETICAO, SENTENCA, ACORDAO, etc. |
| title | TEXT | NO | - | Título do documento |
| content_hash | TEXT | NO | - | SHA-256 do conteúdo |
| file_path | TEXT | YES | NULL | Caminho do arquivo (se externo) |
| content | TEXT | YES | NULL | Conteúdo textual (se armazenado) |
| metadata | TEXT | YES | NULL | JSON com metadados |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de criação |
| created_by | TEXT | YES | NULL | Autor do documento |
| is_current | BOOLEAN | NO | TRUE | Indica versão vigente |

**Constraints**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `case_id` REFERENCES cases(id) ON DELETE CASCADE
- UNIQUE: `case_id, version` (UK_documentos_case_version)
- UNIQUE: `content_hash` (UK_documentos_hash)
- CHECK: `version > 0`

**Índices**:
- `idx_documentos_case_id`: Documentos por caso
- `idx_documentos_type`: Filtragem por tipo
- `idx_documentos_current`: Busca versões vigentes
- `idx_documentos_hash`: Verificação de duplicidade

---

### 3.5 `fontes_url`

**Descrição**: Registro de fontes originais de jurisprudências.

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| id | INTEGER | NO | AUTOINCREMENT | Chave primária |
| url | TEXT | NO | - | URL original |
| source_type | TEXT | NO | - | Tipo: STF, STJ, TSE, etc. |
| content_hash | TEXT | YES | NULL | Hash do conteúdo na última captura |
| last_verified | DATETIME | YES | NULL | Data da última verificação |
| is_valid | BOOLEAN | NO | TRUE | Validade da fonte |
| metadata | TEXT | YES | NULL | JSON com informações adicionais |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de registro |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de atualização |

**Constraints**:
- PRIMARY KEY: `id`
- UNIQUE: `url` (UK_fontes_url_url)
- CHECK: `source_type IN ('STF', 'STJ', 'TSE', 'TRF', 'TJ')`

**Índices**:
- `idx_fontes_url_source`: Filtragem por tribunal
- `idx_fontes_url_valid`: Fontes válidas
- `idx_fontes_url_verified`: Verificação pendente

---

### 3.6 `verbetes_stf`

**Descrição**: Jurisprudências do Supremo Tribunal Federal.

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| id | INTEGER | NO | AUTOINCREMENT | Chave primária |
| source_url_id | INTEGER | YES | NULL | FK para fontes_url |
| theme | TEXT | NO | - | Tema jurídico |
| summary | TEXT | NO | - | Ementa/resumo |
| device | TEXT | YES | NULL | Dispositivo do acórdão |
| rapporteur | TEXT | YES | NULL | Ministro relator |
| judgment_date | DATE | YES | NULL | Data do julgamento |
| publish_date | DATE | YES | NULL | Data de publicação |
| case_number_orig | TEXT | YES | NULL | Número do processo original |
| keywords | TEXT | YES | NULL | Palavras-chave (CSV) |
| metadata | TEXT | YES | NULL | JSON com dados completos |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de inclusão |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de atualização |

**Constraints**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `source_url_id` REFERENCES fontes_url(id) ON DELETE SET NULL
- CHECK: `length(theme) > 0`

**Índices**:
- `idx_verbetes_stf_theme`: Busca por tema
- `idx_verbetes_stf_rapporteur`: Por relator
- `idx_verbetes_stf_judgment_date`: Por data de julgamento
- `idx_verbetes_stf_keywords`: Busca por palavras-chave
- `fts_verbetes_stf_content`: Full-text search (summary, device)

---

### 3.7 `verbetes_stj`

**Descrição**: Jurisprudências do Superior Tribunal de Justiça.

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| id | INTEGER | NO | AUTOINCREMENT | Chave primária |
| source_url_id | INTEGER | YES | NULL | FK para fontes_url |
| theme | TEXT | NO | - | Tema jurídico |
| summary | TEXT | NO | - | Ementa/resumo |
| device | TEXT | YES | NULL | Dispositivo do acórdão |
| rapporteur | TEXT | YES | NULL | Ministro relator |
| judgment_date | DATE | YES | NULL | Data do julgamento |
| publish_date | DATE | YES | NULL | Data de publicação |
| case_number_orig | TEXT | YES | NULL | Número do processo original |
| keywords | TEXT | YES | NULL | Palavras-chave (CSV) |
| metadata | TEXT | YES | NULL | JSON com dados completos |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de inclusão |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de atualização |

**Constraints**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `source_url_id` REFERENCES fontes_url(id) ON DELETE SET NULL
- CHECK: `length(theme) > 0`

**Índices**:
- `idx_verbetes_stj_theme`: Busca por tema
- `idx_verbetes_stj_rapporteur`: Por relator
- `idx_verbetes_stj_judgment_date`: Por data de julgamento
- `idx_verbetes_stj_keywords`: Busca por palavras-chave
- `fts_verbetes_stj_content`: Full-text search (summary, device)

---

### 3.8 `knowledge_cache`

**Descrição**: Cache de chunks de conhecimento para otimização RAG.

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| id | INTEGER | NO | AUTOINCREMENT | Chave primária |
| source_type | TEXT | NO | - | Tipo: VERBETE_STF, VERBETE_STJ, DOCUMENTO, etc. |
| source_id | INTEGER | NO | - | ID da origem |
| chunk_hash | TEXT | NO | - | Hash do chunk |
| content | TEXT | NO | - | Conteúdo do chunk |
| metadata | TEXT | YES | NULL | JSON com contexto |
| embedding | BLOB | YES | NULL | Vetor de embedding (futuro) |
| ttl_seconds | INTEGER | YES | 86400 | Tempo de vida em segundos |
| access_count | INTEGER | NO | 0 | Contador de acessos |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Data de criação |
| expires_at | DATETIME | YES | NULL | Data de expiração |
| last_accessed | DATETIME | YES | NULL | Último acesso |

**Constraints**:
- PRIMARY KEY: `id`
- UNIQUE: `chunk_hash` (UK_knowledge_cache_hash)
- CHECK: `source_type IN ('VERBETE_STF', 'VERBETE_STJ', 'DOCUMENTO', 'CASE', 'EXTERNAL')`

**Índices**:
- `idx_knowledge_cache_source`: Busca por origem
- `idx_knowledge_cache_expires`: Chunks expirados
- `idx_knowledge_cache_access`: Chunks mais acessados
- `idx_knowledge_cache_type`: Filtragem por tipo

---

### 3.9 `system_logs`

**Descrição**: Logs estruturados do sistema para monitoramento.

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| id | INTEGER | NO | AUTOINCREMENT | Chave primária |
| level | TEXT | NO | 'INFO' | Nível: DEBUG, INFO, WARN, ERROR, CRITICAL |
| message | TEXT | NO | - | Mensagem do log |
| context | TEXT | YES | NULL | JSON com contexto da operação |
| performance_ms | INTEGER | YES | NULL | Tempo de execução em ms |
| user_id | TEXT | YES | NULL | Usuário relacionado |
| session_id | TEXT | YES | NULL | Sessão da operação |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Timestamp |

**Constraints**:
- PRIMARY KEY: `id`
- CHECK: `level IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')`

**Índices**:
- `idx_system_logs_level`: Filtragem por nível
- `idx_system_logs_created_at`: Ordenação temporal
- `idx_system_logs_user`: Logs por usuário
- `idx_system_logs_level_date`: Índice composto (level, created_at)

---

### 3.10 `auditlog`

**Descrição**: Registro de auditoria de todas as operações críticas.

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| id | INTEGER | NO | AUTOINCREMENT | Chave primária |
| table_name | TEXT | NO | - | Tabela afetada |
| operation | TEXT | NO | - | Operação: INSERT, UPDATE, DELETE |
| record_id | INTEGER | NO | - | ID do registro afetado |
| old_values | TEXT | YES | NULL | JSON com valores anteriores (UPDATE/DELETE) |
| new_values | TEXT | YES | NULL | JSON com novos valores (INSERT/UPDATE) |
| changed_by | TEXT | YES | NULL | Usuário responsável |
| changed_at | DATETIME | NO | CURRENT_TIMESTAMP | Data da mudança |
| ip_address | TEXT | YES | NULL | IP de origem |
| session_id | TEXT | YES | NULL | Sessão da operação |
| reason | TEXT | YES | NULL | Justificativa da operação |

**Constraints**:
- PRIMARY KEY: `id`
- CHECK: `operation IN ('INSERT', 'UPDATE', 'DELETE')`
- CHECK: `table_name IN ('customers', 'cases', 'case_states', 'documentos', 'verbetes_stf', 'verbetes_stj', 'fontes_url')`

**Índices**:
- `idx_auditlog_table`: Auditoria por tabela
- `idx_auditlog_operation`: Filtragem por operação
- `idx_auditlog_record`: Busca por registro
- `idx_auditlog_changed_at`: Ordenação temporal
- `idx_auditlog_user`: Auditoria por usuário
- `idx_auditlog_table_record`: Índice composto (table_name, record_id)

---

## 4. Views

### 4.1 `vw_customer_history`

**Descrição**: Histórico completo de casos por cliente.

```sql
CREATE VIEW vw_customer_history AS
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
    COUNT(DISTINCT cst.id) AS state_changes_count,
    MAX(cst.changed_at) AS last_state_change
FROM customers c
LEFT JOIN cases cs ON c.id = cs.customer_id AND cs.is_active = 1
LEFT JOIN documentos d ON cs.id = d.case_id AND d.is_current = 1
LEFT JOIN case_states cst ON cs.id = cst.case_id
WHERE c.is_active = 1
GROUP BY c.id, cs.id;
```

---

### 4.2 `vw_audit_cases`

**Descrição**: Auditoria consolidada de operações em casos.

```sql
CREATE VIEW vw_audit_cases AS
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
```

---

### 4.3 `vw_audit_documents`

**Descrição**: Auditoria de operações em documentos.

```sql
CREATE VIEW vw_audit_documents AS
SELECT 
    a.id AS audit_id,
    a.record_id AS document_id,
    d.case_id,
    cs.case_number,
    d.version,
    d.doc_type,
    d.title,
    a.operation,
    a.changed_by,
    a.changed_at,
    CASE 
        WHEN a.operation = 'INSERT' THEN 'Novo documento'
        WHEN a.operation = 'UPDATE' THEN 'Documento modificado'
        WHEN a.operation = 'DELETE' THEN 'Documento removido'
    END AS change_description
FROM auditlog a
LEFT JOIN documentos d ON a.record_id = d.id
LEFT JOIN cases cs ON d.case_id = cs.id
WHERE a.table_name = 'documentos'
ORDER BY a.changed_at DESC;
```

---

### 4.4 `vw_recent_changes`

**Descrição**: Últimas alterações no sistema (últimas 24h).

```sql
CREATE VIEW vw_recent_changes AS
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
```

---

### 4.5 `vw_case_timeline`

**Descrição**: Linha do tempo completa de um caso.

```sql
CREATE VIEW vw_case_timeline AS
SELECT 
    cs.id AS case_id,
    cs.case_number,
    c.name AS customer_name,
    'STATUS_CHANGE' AS event_type,
    cst.status AS event_value,
    cst.description,
    cst.changed_at AS event_date,
    cst.changed_by
FROM cases cs
JOIN customers c ON cs.customer_id = c.id
JOIN case_states cst ON cs.id = cst.case_id

UNION ALL

SELECT 
    cs.id AS case_id,
    cs.case_number,
    c.name AS customer_name,
    'DOCUMENT_ADDED' AS event_type,
    d.doc_type || ' - v' || d.version AS event_value,
    d.title AS description,
    d.created_at AS event_date,
    d.created_by
FROM cases cs
JOIN customers c ON cs.customer_id = c.id
JOIN documentos d ON cs.id = d.case_id

ORDER BY event_date DESC;
```

---

### 4.6 `vw_knowledge_stats`

**Descrição**: Estatísticas de cache de conhecimento.

```sql
CREATE VIEW vw_knowledge_stats AS
SELECT 
    source_type,
    COUNT(*) AS total_chunks,
    SUM(access_count) AS total_accesses,
    AVG(access_count) AS avg_accesses,
    COUNT(CASE WHEN expires_at < datetime('now') THEN 1 END) AS expired_chunks,
    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) AS chunks_with_embedding,
    MIN(created_at) AS oldest_chunk,
    MAX(created_at) AS newest_chunk
FROM knowledge_cache
GROUP BY source_type;
```

---

## 5. Triggers

### 5.1 `trg_audit_customers`

**Descrição**: Auditoria automática de mudanças em customers.

```sql
CREATE TRIGGER trg_audit_customers_after_update
AFTER UPDATE ON customers
FOR EACH ROW
BEGIN
    INSERT INTO auditlog (
        table_name, operation, record_id, 
        old_values, new_values, changed_by, changed_at
    )
    VALUES (
        'customers', 'UPDATE', OLD.id,
        json_object(
            'name', OLD.name,
            'document', OLD.document,
            'email', OLD.email,
            'phone', OLD.phone,
            'is_active', OLD.is_active
        ),
        json_object(
            'name', NEW.name,
            'document', NEW.document,
            'email', NEW.email,
            'phone', NEW.phone,
            'is_active', NEW.is_active
        ),
        COALESCE(NEW.updated_by, 'system'),
        datetime('now')
    );
END;

CREATE TRIGGER trg_audit_customers_after_delete
AFTER DELETE ON customers
FOR EACH ROW
BEGIN
    INSERT INTO auditlog (
        table_name, operation, record_id,
        old_values, changed_by, changed_at
    )
    VALUES (
        'customers', 'DELETE', OLD.id,
        json_object(
            'name', OLD.name,
            'document', OLD.document,
            'email', OLD.email
        ),
        'system',
        datetime('now')
    );
END;
```

---

### 5.2 `trg_audit_cases`

**Descrição**: Auditoria automática de mudanças em cases.

```sql
CREATE TRIGGER trg_audit_cases_after_update
AFTER UPDATE ON cases
FOR EACH ROW
WHEN OLD.status != NEW.status OR OLD.is_active != NEW.is_active
BEGIN
    INSERT INTO auditlog (
        table_name, operation, record_id,
        old_values, new_values, changed_by, changed_at, reason
    )
    VALUES (
        'cases', 'UPDATE', OLD.id,
        json_object('status', OLD.status, 'is_active', OLD.is_active),
        json_object('status', NEW.status, 'is_active', NEW.is_active),
        COALESCE(NEW.updated_by, 'system'),
        datetime('now'),
        'Mudança de status ou ativação'
    );
END;
```

---

### 5.3 `trg_audit_documentos`

**Descrição**: Auditoria automática de documentos.

```sql
CREATE TRIGGER trg_audit_documentos_after_insert
AFTER INSERT ON documentos
FOR EACH ROW
BEGIN
    INSERT INTO auditlog (
        table_name, operation, record_id,
        new_values, changed_by, changed_at
    )
    VALUES (
        'documentos', 'INSERT', NEW.id,
        json_object(
            'case_id', NEW.case_id,
            'version', NEW.version,
            'doc_type', NEW.doc_type,
            'title', NEW.title
        ),
        COALESCE(NEW.created_by, 'system'),
        datetime('now')
    );
END;

CREATE TRIGGER trg_audit_documentos_after_delete
AFTER DELETE ON documentos
FOR EACH ROW
BEGIN
    INSERT INTO auditlog (
        table_name, operation, record_id,
        old_values, changed_by, changed_at
    )
    VALUES (
        'documentos', 'DELETE', OLD.id,
        json_object(
            'case_id', OLD.case_id,
            'version', OLD.version,
            'doc_type', OLD.doc_type,
            'title', OLD.title
        ),
        'system',
        datetime('now')
    );
END;
```

---

### 5.4 `trg_update_timestamps`

**Descrição**: Atualização automática de timestamps.

```sql
-- Customers
CREATE TRIGGER trg_customers_update_timestamp
BEFORE UPDATE ON customers
FOR EACH ROW
BEGIN
    NEW.updated_at = datetime('now');
END;

-- Cases
CREATE TRIGGER trg_cases_update_timestamp
BEFORE UPDATE ON cases
FOR EACH ROW
BEGIN
    NEW.updated_at = datetime('now');
END;

-- Fontes URL
CREATE TRIGGER trg_fontes_url_update_timestamp
BEFORE UPDATE ON fontes_url
FOR EACH ROW
BEGIN
    NEW.updated_at = datetime('now');
END;

-- Verbetes STF
CREATE TRIGGER trg_verbetes_stf_update_timestamp
BEFORE UPDATE ON verbetes_stf
FOR EACH ROW
BEGIN
    NEW.updated_at = datetime('now');
END;

-- Verbetes STJ
CREATE TRIGGER trg_verbetes_stj_update_timestamp
BEFORE UPDATE ON verbetes_stj
FOR EACH ROW
BEGIN
    NEW.updated_at = datetime('now');
END;
```

---

### 5.5 `trg_auto_version_documents`

**Descrição**: Versionamento automático de documentos.

```sql
CREATE TRIGGER trg_documentos_auto_version
BEFORE INSERT ON documentos
FOR EACH ROW
WHEN NEW.version IS NULL OR NEW.version = 0
BEGIN
    SELECT RAISE(ABORT, 'Versionamento automático não suportado via trigger. Use a aplicação.')
    WHERE NEW.version IS NULL OR NEW.version = 0;
END;
```

*Nota: O versionamento é gerenciado pela camada de aplicação para maior controle.*

---

### 5.6 `trg_invalidate_old_versions`

**Descrição**: Invalida versões anteriores ao inserir nova versão.

```sql
CREATE TRIGGER trg_documentos_invalidate_previous
AFTER INSERT ON documentos
FOR EACH ROW
BEGIN
    UPDATE documentos
    SET is_current = 0
    WHERE case_id = NEW.case_id
      AND doc_type = NEW.doc_type
      AND id != NEW.id
      AND is_current = 1;
END;
```

---

## 6. Tipos de Variáveis e Atributos

### 6.1 Tipos de Dados SQLite Utilizados

| Tipo SQLite | Uso | Exemplo |
|-------------|-----|---------|
| INTEGER | IDs, contadores, booleanos | id, version, is_active |
| TEXT | Strings, JSON, datas | name, email, metadata |
| REAL | Valores decimais (não usado atualmente) | - |
| BLOB | Embeddings vetoriais (futuro) | embedding |
| DATETIME | Timestamps | created_at, updated_at |

### 6.2 Padrões de Nomenclatura

- **Tabelas**: snake_case, plural (ex: `customers`, `case_states`)
- **Colunas**: snake_case, singular (ex: `created_at`, `case_number`)
- **Chaves Primárias**: `id`
- **Chaves Estrangeiras**: `{tabela}_id` (ex: `customer_id`)
- **Índices**: `idx_{tabela}_{colunas}` (ex: `idx_cases_status`)
- **Views**: `vw_{descricao}` (ex: `vw_customer_history`)
- **Triggers**: `trg_{tabela}_{evento}` (ex: `trg_audit_cases_after_update`)
- **Constraints**: `{tipo}_{tabela}_{colunas}` (ex: `UK_customers_document`)

### 6.3 Convenções de JSON

Campos `metadata` armazenam JSON com as seguintes convenções:

```json
{
  "chave": "valor",
  "nested": {
    "objeto": "valor"
  },
  "lista": ["item1", "item2"]
}
```

**Regras**:
- Keys em snake_case
- Sem caracteres especiais
- Encoding UTF-8 obrigatório

---

## 7. Relacionamentos

### 7.1 Diagrama Detalhado

```
customers (1) ──────< (N) cases
    │                    │
    │                    ├──────< (N) case_states
    │                    │
    │                    └──────< (N) documentos
    │
    └── (via auditlog) ── Monitoramento de mudanças

fontes_url (1) ─────< (N) verbetes_stf
    │
    └───── (1) ─────< (N) verbetes_stj

cases ── (via knowledge_cache) ── Cache de conhecimento

auditlog ── (monitora) ──> todas as tabelas principais
```

### 7.2 Cardinalidade

| Relacionamento | Tipo | Descrição |
|---------------|------|-----------|
| customers → cases | 1:N | Um cliente tem muitos casos |
| cases → case_states | 1:N | Um caso tem muitos estados históricos |
| cases → documentos | 1:N | Um caso tem muitos documentos |
| fontes_url → verbetes_stf | 1:N | Uma fonte origina muitos verbetes STF |
| fontes_url → verbetes_stj | 1:N | Uma fonte origina muitos verbetes STJ |
| auditlog → todas | N:1 | Muitos logs referenciam um registro |

### 7.3 Regras de Integridade

- **CASCADE DELETE**: Remoção de customer remove todos os casos associados
- **CASCADE DELETE**: Remoção de caso remove states e documentos
- **SET NULL**: Remoção de fonte_url mantém verbetes (perde referência)
- **RESTRICT**: Não permitir exclusão de registros com dependências ativas

---

## 8. Queries Principais

### 8.1 CRUD - Customers

```sql
-- CREATE
INSERT INTO customers (type, name, document, email, phone, address, metadata)
VALUES ('PF', 'João Silva', '12345678901', 'joao@email.com', '11999999999', 
        'Rua X, 123', '{"observacao": "Cliente especial"}');

-- READ
SELECT * FROM customers WHERE document = '12345678901';
SELECT * FROM vw_customer_history WHERE customer_id = 1;

-- UPDATE
UPDATE customers 
SET email = 'novo@email.com', updated_by = 'admin'
WHERE id = 1;

-- DELETE (soft delete)
UPDATE customers SET is_active = 0 WHERE id = 1;
```

### 8.2 CRUD - Cases

```sql
-- CREATE
INSERT INTO cases (customer_id, case_number, court, class, status, subject, description)
VALUES (1, '0012345-67.2024.8.26.0001', '1ª Vara Cível', 'Procedimento Comum', 
        'ATIVO', 'Danos Morais', 'Descrição do caso...');

-- READ com histórico
SELECT cs.*, c.name as customer_name
FROM cases cs
JOIN customers c ON cs.customer_id = c.id
WHERE cs.case_number = '0012345-67.2024.8.26.0001';

-- Timeline do caso
SELECT * FROM vw_case_timeline WHERE case_id = 1 ORDER BY event_date DESC;

-- UPDATE status (cria entry em case_states automaticamente via aplicação)
UPDATE cases SET status = 'SUSPENSO', updated_by = 'advogado1' WHERE id = 1;

-- DELETE (soft delete)
UPDATE cases SET is_active = 0 WHERE id = 1;
```

### 8.3 CRUD - Documentos

```sql
-- CREATE (nova versão)
INSERT INTO documentos (case_id, version, doc_type, title, content_hash, content, created_by, is_current)
VALUES (1, 2, 'PETICAO', 'Petição Inicial', 'sha256...', 'Conteúdo...', 'advogado1', 1);

-- READ versão atual
SELECT * FROM documentos WHERE case_id = 1 AND is_current = 1;

-- READ todas as versões
SELECT * FROM documentos WHERE case_id = 1 ORDER BY version DESC;

-- UPDATE (cria nova versão, não modifica existente)
-- Aplicação deve criar novo registro com version+1

-- DELETE (soft delete via metadata)
UPDATE documentos SET metadata = json_set(metadata, '$.deleted', true) WHERE id = 1;
```

### 8.4 Busca - Verbetes

```sql
-- Busca por tema STF
SELECT * FROM verbetes_stf 
WHERE theme LIKE '%DANO MORAL%' 
ORDER BY judgment_date DESC;

-- Busca full-text
SELECT * FROM verbetes_stf 
WHERE summary LIKE '%palavra-chave%' 
   OR device LIKE '%palavra-chave%';

-- Busca por período
SELECT * FROM verbetes_stj 
WHERE judgment_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND theme = 'RESPONSABILIDADE CIVIL';

-- Busca por relator
SELECT * FROM verbetes_stf 
WHERE rapporteur LIKE '%BARROSO%' 
ORDER BY publish_date DESC;
```

### 8.5 Auditoria

```sql
-- Histórico de mudanças de um caso
SELECT * FROM vw_audit_cases WHERE case_id = 1 ORDER BY changed_at DESC;

-- Últimas alterações do sistema
SELECT * FROM vw_recent_changes LIMIT 50;

-- Auditoria por usuário
SELECT * FROM auditlog WHERE changed_by = 'advogado1' 
ORDER BY changed_at DESC;

-- Estatísticas de auditoria
SELECT 
    table_name, 
    operation, 
    COUNT(*) as qtd,
    DATE(changed_at) as data
FROM auditlog 
GROUP BY table_name, operation, DATE(changed_at)
ORDER BY data DESC, qtd DESC;
```

### 8.6 Knowledge Cache

```sql
-- Inserir chunk
INSERT INTO knowledge_cache (source_type, source_id, chunk_hash, content, metadata, ttl_seconds, expires_at)
VALUES ('VERBETE_STF', 1, 'hash123', 'Conteúdo do chunk...', '{}', 86400, datetime('now', '+1 day'));

-- Buscar chunk válido
SELECT * FROM knowledge_cache 
WHERE chunk_hash = 'hash123' 
  AND (expires_at IS NULL OR expires_at > datetime('now'));

-- Limpar expirados
DELETE FROM knowledge_cache WHERE expires_at < datetime('now');

-- Estatísticas
SELECT * FROM vw_knowledge_stats;
```

### 8.7 Logs do Sistema

```sql
-- Erros nas últimas 24h
SELECT * FROM system_logs 
WHERE level IN ('ERROR', 'CRITICAL') 
  AND created_at >= datetime('now', '-1 day')
ORDER BY created_at DESC;

-- Performance de operações
SELECT 
    message,
    AVG(performance_ms) as avg_ms,
    MAX(performance_ms) as max_ms,
    COUNT(*) as qtd
FROM system_logs 
WHERE performance_ms IS NOT NULL
GROUP BY message
ORDER BY avg_ms DESC
LIMIT 20;

-- Logs por sessão
SELECT * FROM system_logs WHERE session_id = 'session-xyz' ORDER BY created_at;
```

---

## 9. Constraints e Validações

### 9.1 Constraints de Integridade Referencial

```sql
-- Todas as FKs usam ON DELETE CASCADE ou SET NULL
FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
FOREIGN KEY (source_url_id) REFERENCES fontes_url(id) ON DELETE SET NULL
```

### 9.2 Check Constraints

```sql
-- Tipo de pessoa
CHECK (type IN ('PF', 'PJ'))

-- Status de caso
CHECK (status IN ('ATIVO', 'SUSPENSO', 'ARQUIVADO', 'ENCERRADO'))

-- Nível de log
CHECK (level IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'))

-- Operação de auditoria
CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE'))

-- Tipo de fonte
CHECK (source_type IN ('STF', 'STJ', 'TSE', 'TRF', 'TJ'))

-- Tamanho do documento (CPF/CNPJ)
CHECK (length(document) IN (11, 14))
```

### 9.3 Unique Constraints

```sql
-- Documentos únicos
UNIQUE (document) -- customers
UNIQUE (case_number) -- cases
UNIQUE (case_id, version) -- documentos
UNIQUE (url) -- fontes_url
UNIQUE (chunk_hash) -- knowledge_cache
```

---

## 10. Índices

### 10.1 Índices Simples

| Nome | Tabela | Coluna(s) | Propósito |
|------|--------|-----------|-----------|
| idx_customers_document | customers | document | Busca por CPF/CNPJ |
| idx_customers_type | customers | type | Filtragem PF/PJ |
| idx_cases_customer_id | cases | customer_id | Casos por cliente |
| idx_cases_number | cases | case_number | Busca processual |
| idx_cases_status | cases | status | Filtragem por status |
| idx_case_states_case_id | case_states | case_id | Histórico por caso |
| idx_documentos_case_id | documentos | case_id | Docs por caso |
| idx_verbetes_stf_theme | verbetes_stf | theme | Busca por tema |
| idx_verbetes_stj_theme | verbetes_stj | theme | Busca por tema |
| idx_fontes_url_source | fontes_url | source_type | Filtragem por tribunal |
| idx_knowledge_cache_source | knowledge_cache | source_type | Cache por origem |
| idx_system_logs_level | system_logs | level | Filtragem por nível |
| idx_auditlog_table | auditlog | table_name | Auditoria por tabela |

### 10.2 Índices Compostos

| Nome | Tabela | Coluna(s) | Propósito |
|------|--------|-----------|-----------|
| idx_cases_customer_status | cases | customer_id, status | Casos ativos por cliente |
| idx_documentos_case_version | documentos | case_id, version | Versões por caso |
| idx_system_logs_level_date | system_logs | level, created_at | Logs filtrados por período |
| idx_auditlog_table_record | auditlog | table_name, record_id | Auditoria específica |
| idx_knowledge_cache_type_expiry | knowledge_cache | source_type, expires_at | Cache válido por tipo |

### 10.3 Full-Text Search

```sql
-- FTS5 para verbetes STF
CREATE VIRTUAL TABLE fts_verbetes_stf_content USING fts5(
    summary,
    device,
    content='verbetes_stf',
    content_rowid='id'
);

-- FTS5 para verbetes STJ
CREATE VIRTUAL TABLE fts_verbetes_stj_content USING fts5(
    summary,
    device,
    content='verbetes_stj',
    content_rowid='id'
);
```

---

## 11. Configurações do SQLite

### 11.1 PRAGMA Recommendations

```sql
-- Habilitar WAL mode para concorrência
PRAGMA journal_mode = WAL;

-- Synchronous normal (balance performance/segurança)
PRAGMA synchronous = NORMAL;

-- Cache size (2000 páginas = ~8MB)
PRAGMA cache_size = -2000;

-- Foreign keys habilitadas
PRAGMA foreign_keys = ON;

-- Temp store em memória
PRAGMA temp_store = MEMORY;

-- Mmap para performance de leitura
PRAGMA mmap_size = 268435456; -- 256MB

-- Auto vacuum incremental
PRAGMA auto_vacuum = INCREMENTAL;

-- Busy timeout (5 segundos)
PRAGMA busy_timeout = 5000;
```

### 11.2 Configuração Recomendada (Python)

```python
import sqlite3

def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA cache_size = -2000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn
```

---

## 12. Scripts de Manutenção

### 12.1 Vacuum e Analyze

```sql
-- Vacuum completo (recomendado periodicamente)
VACUUM;

-- Analyze para otimizar queries
ANALYZE;

-- Incremental vacuum (WAL mode)
PRAGMA wal_checkpoint(TRUNCATE);
```

### 12.2 Limpeza de Logs Antigos

```sql
-- Remover logs de sistema com mais de 90 dias
DELETE FROM system_logs 
WHERE created_at < datetime('now', '-90 days')
  AND level NOT IN ('ERROR', 'CRITICAL');

-- Remover auditlog com mais de 2 anos (manter críticos)
DELETE FROM auditlog 
WHERE changed_at < datetime('now', '-2 years')
  AND table_name NOT IN ('customers', 'cases');

-- Remover knowledge cache expirado
DELETE FROM knowledge_cache 
WHERE expires_at < datetime('now');
```

### 12.3 Backup

```bash
#!/bin/bash
# backup.sh
DB_PATH="data/db/agente_juridico.db"
BACKUP_DIR="data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/backup_$TIMESTAMP.db'"
echo "Backup criado: backup_$TIMESTAMP.db"

# Manter apenas últimos 7 backups
ls -t $BACKUP_DIR/backup_*.db | tail -n +8 | xargs rm -f
```

### 12.4 Verificação de Integridade

```sql
-- Verificar integridade do banco
PRAGMA integrity_check;

-- Verificar foreign keys
PRAGMA foreign_key_check;

-- Verificar quick check
PRAGMA quick_check;
```

---

## 13. Segurança

### 13.1 Melhores Práticas

1. **Criptografia**: Usar SQLCipher para criptografia em repouso
2. **Backup**: Backups diários com retenção de 30 dias
3. **Acesso**: Restringir permissões de escrita ao mínimo necessário
4. **Auditoria**: Manter auditlog ativo em todas as tabelas sensíveis
5. **Sanitização**: Validar todos os inputs antes de inserir no banco

### 13.2 Dados Sensíveis

- CPF/CNPJ: Armazenar apenas números, sem máscara
- Endereços: Considerar criptografia se necessário
- Logs: Evitar registrar dados pessoais completos
- Metadata: Validar JSON antes de armazenar

### 13.3 Controle de Acesso (Aplicação)

```python
# Exemplo de validação de acesso
def can_access_case(user_id: str, case_id: int) -> bool:
    # Verificar se usuário tem permissão no caso
    pass

def log_audit_operation(table: str, operation: str, record_id: int, 
                       user_id: str, old_values: dict, new_values: dict):
    # Registrar no auditlog
    pass
```

---

## 14. Performance

### 14.1 Otimizações Implementadas

- Índices em colunas de busca frequente
- WAL mode para concorrência de leitura/escrita
- Cache de queries frequentes (knowledge_cache)
- Prepared statements para operações repetitivas
- Transações agrupadas para inserts em lote

### 14.2 Query Optimization Tips

```sql
-- EVITAR: SELECT * em produção
SELECT * FROM cases;

-- PREFERIR: Colunas específicas
SELECT id, case_number, status FROM cases;

-- EVITAR: LIKE com wildcard no início
WHERE name LIKE '%Silva%';

-- PREFERIR: Full-text search
WHERE name MATCH 'Silva';

-- EVITAR: Subqueries correlacionadas
-- PREFERIR: JOINs ou CTEs
```

### 14.3 Monitoring

```sql
-- Queries mais lentas (requer extensão)
SELECT * FROM system_logs 
WHERE performance_ms > 1000 
ORDER BY performance_ms DESC 
LIMIT 10;

-- Tamanho das tabelas
SELECT 
    name AS table_name,
    pgsize * pages AS size_bytes
FROM dbstat 
GROUP BY name
ORDER BY size_bytes DESC;
```

---

## 15. Apêndice

### 15.1 Glossário

- **RAG**: Retrieval-Augmented Generation
- **FTS**: Full-Text Search
- **WAL**: Write-Ahead Logging
- **FK**: Foreign Key
- **PK**: Primary Key
- **UK**: Unique Key
- **CSV**: Comma-Separated Values

### 15.2 Referências

- [Documentação SQLite](https://www.sqlite.org/docs.html)
- [SQLite Best Practices](https://www.sqlite.org/np1queryprob.html)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)

### 15.3 Histórico de Revisões

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0.0 | 2024 | Equipe | Versão inicial |
| 1.1.0 | Em desenvolvimento | Equipe | Adição de auditlog e triggers |

---

*Documento criado para o projeto Agente Jurídico IA*
*Última atualização: 2024*
