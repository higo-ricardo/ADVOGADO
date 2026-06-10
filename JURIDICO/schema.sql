-- ============================================
-- Schema do Banco de Dados - Agente Jurídico IA
-- ============================================
-- 4 Tabelas Principais: customers, cases, legal_templates, knowledge_chunks
-- Sistema de ranking inteligente para knowledge_chunks
-- Templates de petições para uso pelo LLM
-- ============================================

-- Habilitar foreign keys
PRAGMA foreign_keys = ON;

-- ============================================
-- 1. Tabela: customers (Clientes)
-- ============================================
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('PF', 'PJ')),
    name TEXT NOT NULL,
    document TEXT UNIQUE NOT NULL, -- CPF ou CNPJ
    email TEXT,
    phone TEXT,
    address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Índices para customers
CREATE INDEX IF NOT EXISTS idx_customers_document ON customers(document);
CREATE INDEX IF NOT EXISTS idx_customers_type ON customers(type);
CREATE INDEX IF NOT EXISTS idx_customers_active ON customers(is_active);

-- ============================================
-- 2. Tabela: cases (Casos Jurídicos)
-- ============================================
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    case_number TEXT, -- Número do processo
    case_type TEXT NOT NULL, -- Ex: "Habeas Corpus", "Apelação"
    court TEXT, -- Vara/Órgão julgador
    state TEXT NOT NULL DEFAULT 'INITIATED',
    priority INTEGER DEFAULT 5 CHECK(priority BETWEEN 1 AND 10),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Índices para cases
CREATE INDEX IF NOT EXISTS idx_cases_customer ON cases(customer_id);
CREATE INDEX IF NOT EXISTS idx_cases_state ON cases(state);
CREATE INDEX IF NOT EXISTS idx_cases_type ON cases(case_type);
CREATE INDEX IF NOT EXISTS idx_cases_priority ON cases(priority DESC);

-- ============================================
-- 3. Tabela: legal_templates (Templates de Petições)
-- ============================================
-- Armazena schemas/templates das petições (arquivos minutas-*)
-- O LLM usa este template como base para gerar petições
-- NÃO armazena as petições geradas, apenas o template
CREATE TABLE IF NOT EXISTS legal_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT UNIQUE NOT NULL, -- Ex: "minuta_habeas_corpus"
    template_type TEXT NOT NULL, -- Ex: "habeas_corpus", "apelacao_criminal"
    structure_json TEXT NOT NULL, -- Estrutura JSON do template
    variables_schema TEXT NOT NULL, -- Schema das variáveis que o LLM deve preencher
    description TEXT,
    version TEXT DEFAULT '1.0',
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0, -- Quantas vezes foi usado
    last_used_at DATETIME
);

-- Índices para legal_templates
CREATE INDEX IF NOT EXISTS idx_templates_type ON legal_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_templates_active ON legal_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_templates_usage ON legal_templates(usage_count DESC);

-- ============================================
-- 4. Tabela: knowledge_chunks (Base de Conhecimento RAG)
-- ============================================
-- Chunks de documentos jurídicos com metadados e ranking inteligente
-- Sistema de feedback: success_count, fail_count, usage_count
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL CHECK(source_type IN ('STF', 'STJ', 'TJ', 'LEI', 'DOCTRINE')),
    source_id TEXT, -- ID original na fonte
    chunk_hash TEXT UNIQUE NOT NULL, -- Hash para deduplicação
    topic TEXT NOT NULL, -- Tópico principal (ex: "habeas corpus", "prisão preventiva")
    tags TEXT, -- Tags separadas por vírgula (ex: "CPP,prisão,liberdade")
    content TEXT NOT NULL, -- Conteúdo do chunk
    metadata_json TEXT, -- Metadados adicionais em JSON
    
    -- Sistema de Ranking Inteligente
    usage_count INTEGER DEFAULT 0, -- Total de usos
    success_count INTEGER DEFAULT 0, -- Quantas vezes foi útil/aceito
    fail_count INTEGER DEFAULT 0, -- Quantas vezes foi rejeitado
    last_used_at DATETIME,
    
    -- Score calculado dinamicamente
    relevance_score REAL DEFAULT 50.0 CHECK(relevance_score BETWEEN 0 AND 100),
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para knowledge_chunks (CRÍTICO para performance RAG)
CREATE INDEX IF NOT EXISTS idx_chunks_topic ON knowledge_chunks(topic);
CREATE INDEX IF NOT EXISTS idx_chunks_tags ON knowledge_chunks(tags);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON knowledge_chunks(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_chunks_hash ON knowledge_chunks(chunk_hash);
CREATE INDEX IF NOT EXISTS idx_chunks_relevance ON knowledge_chunks(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_chunks_usage ON knowledge_chunks(usage_count DESC);
CREATE INDEX IF NOT EXISTS idx_chunks_last_used ON knowledge_chunks(last_used_at);
CREATE INDEX IF NOT EXISTS idx_chunks_success_rate ON knowledge_chunks(success_count DESC, fail_count ASC);

-- ============================================
-- Views Úteis
-- ============================================

-- View: Top chunks mais úteis por tópico (com taxa de sucesso)
CREATE VIEW IF NOT EXISTS vw_top_chunks AS
SELECT 
    id,
    topic,
    tags,
    source_type,
    usage_count,
    success_count,
    fail_count,
    CASE 
        WHEN (success_count + fail_count) > 0 
        THEN ROUND(success_count * 100.0 / (success_count + fail_count), 2)
        ELSE 0 
    END as success_rate,
    relevance_score,
    last_used_at,
    created_at
FROM knowledge_chunks
ORDER BY success_rate DESC, usage_count DESC, relevance_score DESC;

-- View: Estatísticas de templates
CREATE VIEW IF NOT EXISTS vw_template_stats AS
SELECT 
    id,
    template_name,
    template_type,
    usage_count,
    last_used_at,
    version,
    is_active
FROM legal_templates
ORDER BY usage_count DESC;

-- View: Casos ativos por cliente
CREATE VIEW IF NOT EXISTS vw_active_cases AS
SELECT 
    c.id,
    c.case_number,
    c.case_type,
    c.state,
    c.priority,
    cust.name as customer_name,
    cust.document as customer_document,
    c.created_at,
    c.updated_at
FROM cases c
JOIN customers cust ON c.customer_id = cust.id
WHERE c.closed_at IS NULL
ORDER BY c.priority DESC, c.created_at DESC;

-- View: Histórico completo de casos (incluídos fechados)
CREATE VIEW IF NOT EXISTS vw_case_history AS
SELECT 
    c.id,
    c.case_number,
    c.case_type,
    c.state,
    c.closed_at,
    cust.name as customer_name,
    cust.document as customer_document,
    c.created_at,
    julianday('now') - julianday(c.created_at) as days_since_created,
    CASE 
        WHEN c.closed_at IS NOT NULL 
        THEN julianday(c.closed_at) - julianday(c.created_at)
        ELSE NULL 
    END as days_to_close
FROM cases c
JOIN customers cust ON c.customer_id = cust.id
ORDER BY c.created_at DESC;

-- View: Chunk stats agregados por tópico
CREATE VIEW IF NOT EXISTS vw_topic_stats AS
SELECT 
    topic,
    COUNT(*) as total_chunks,
    SUM(usage_count) as total_uses,
    SUM(success_count) as total_successes,
    SUM(fail_count) as total_fails,
    CASE 
        WHEN (SUM(success_count) + SUM(fail_count)) > 0 
        THEN ROUND(SUM(success_count) * 100.0 / (SUM(success_count) + SUM(fail_count)), 2)
        ELSE 0 
    END as overall_success_rate,
    AVG(relevance_score) as avg_relevance
FROM knowledge_chunks
GROUP BY topic
ORDER BY total_uses DESC;

-- ============================================
-- Triggers para Atualização Automática
-- ============================================

-- Trigger: Atualizar updated_at em customers
CREATE TRIGGER IF NOT EXISTS trg_customers_updated_at
AFTER UPDATE ON customers
BEGIN
    UPDATE customers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger: Atualizar updated_at em cases
CREATE TRIGGER IF NOT EXISTS trg_cases_updated_at
AFTER UPDATE ON cases
BEGIN
    UPDATE cases SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger: Atualizar updated_at em legal_templates
CREATE TRIGGER IF NOT EXISTS trg_templates_updated_at
AFTER UPDATE ON legal_templates
BEGIN
    UPDATE legal_templates SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger: Atualizar updated_at em knowledge_chunks
CREATE TRIGGER IF NOT EXISTS trg_chunks_updated_at
AFTER UPDATE ON knowledge_chunks
BEGIN
    UPDATE knowledge_chunks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================
-- Dados Iniciais (Seed)
-- ============================================

-- Inserir templates básicos (exemplos)
INSERT OR IGNORE INTO legal_templates (template_name, template_type, structure_json, variables_schema, description) VALUES
('minuta_habeas_corpus', 'habeas_corpus', 
 '{"sections": ["cabecalho", "fatos", "fundamentacao", "pedido"], "structure": "standard"}',
 '{"variables": ["paciente_nome", "paciente_documento", "autoridade_coatora", "fato_descricao", "fundamento_legal"]}',
 'Template padrão para Habeas Corpus Criminal'),

('minuta_apelacao', 'apelacao_criminal',
 '{"sections": ["cabecalho", "sintese", "merito", "pedido"], "structure": "standard"}',
 '{"variables": ["apelante_nome", "apelante_documento", "processo_numero", "sentenca_data", "argumentos"]}',
 'Template padrão para Apelação Criminal'),

('minuta_revogacao_prisao', 'revogacao_prisao',
 '{"sections": ["cabecalho", "fatos", "direito", "pedido"], "structure": "standard"}',
 '{"variables": ["preso_nome", "preso_documento", "processo_numero", "vara", "argumentos_revogacao"]}',
 'Template para Revogação de Prisão Preventiva');

-- ============================================
-- Comentários e Documentação
-- ============================================

-- Nota: Este schema utiliza SQLite como banco de dados
-- Para produção, considere:
-- 1. Criptografia de dados sensíveis (document, email, phone)
-- 2. Backup automático periódico
-- 3. WAL mode para melhor performance: PRAGMA journal_mode = WAL;
-- 4. VACUUM periódico para otimização

-- Configurações recomendadas para produção
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = memory;
PRAGMA busy_timeout = 5000;

-- ============================================
-- Fim do Schema
-- ============================================
