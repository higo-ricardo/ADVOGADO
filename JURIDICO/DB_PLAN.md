# Plano de Banco de Dados - Agente Jurídico IA

## 📋 Visão Geral
Sistema de banco de dados otimizado para gerenciamento de casos jurídicos, templates de petições e base de conhecimento RAG com ranking inteligente.

## 🏗️ Arquitetura

### 4 Tabelas Principais

#### 1. `customers` - Clientes
Armazena informações de clientes (PF/PJ) com suporte a LGPD.

```sql
CREATE TABLE customers (
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
```

#### 2. `cases` - Casos Jurídicos
Gerencia casos com máquina de estados e histórico.

```sql
CREATE TABLE cases (
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
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

#### 3. `legal_templates` - Templates de Petições
**NOVO**: Armazena schemas/templates das petições (arquivos `minutas-*`) para uso pelo LLM.

```sql
CREATE TABLE legal_templates (
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
```

**Como o LLM usa:**
1. Recupera o template pelo `template_type`
2. Lê `structure_json` para entender a estrutura da petição
3. Lê `variables_schema` para saber quais dados precisa preencher
4. Gera a petição final combinando template + dados do caso + jurisprudência
5. **Não armazena** a petição gerada (apenas usa o template como base)

#### 4. `knowledge_chunks` - Base de Conhecimento RAG
Chunks de documentos jurídicos com metadados e **ranking inteligente**.

```sql
CREATE TABLE knowledge_chunks (
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
```

### 🔍 Sistema de Ranking Inteligente

O ranking dos chunks é calculado com base em múltiplos fatores:

```python
def calculate_ranking(chunk):
    """
    Fórmula de ranking dinâmico:
    
    score_base = (success_rate * 40) + (usage_factor * 20) + (recency_factor * 25) + (relevance_context * 15)
    
    Onde:
    - success_rate = success_count / (success_count + fail_count + 1) * 100
    - usage_factor = log(usage_count + 1) * 10
    - recency_factor = dias_desde_ultimo_uso (decai 0.5 pontos/dia após 7 dias)
    - relevance_context = score baseado no match de topic/tags com a query
    """
    pass
```

**Métricas de Ranking:**
- ✅ **Taxa de Sucesso**: `(success_count / total_uses) * 40 pontos`
- ✅ **Volume de Uso**: `log(usage_count) * 20 pontos` (satura em alto uso)
- ✅ **Recência**: `-0.5 pontos/dia` após 7 dias sem uso (máx -25 pontos)
- ✅ **Relevância Contextual**: Match de topic/tags com a query (0-15 pontos)

**Atualização Automática:**
- `success_count++`: Quando o usuário aceita/utiliza o chunk gerado
- `fail_count++`: Quando o usuário rejeita/substitui o chunk
- `usage_count++`: Sempre que o chunk é recuperado
- `last_used_at`: Atualizado a cada uso
- `relevance_score`: Recalculado periodicamente ou sob demanda

## 📊 Views Úteis

```sql
-- Top chunks mais úteis por tópico
CREATE VIEW vw_top_chunks AS
SELECT 
    topic,
    tags,
    usage_count,
    success_count,
    fail_count,
    CASE 
        WHEN (success_count + fail_count) > 0 
        THEN ROUND(success_count * 100.0 / (success_count + fail_count), 2)
        ELSE 0 
    END as success_rate,
    last_used_at
FROM knowledge_chunks
WHERE is_active = 1
ORDER BY success_rate DESC, usage_count DESC;

-- Estatísticas de templates
CREATE VIEW vw_template_stats AS
SELECT 
    template_name,
    template_type,
    usage_count,
    last_used_at,
    version
FROM legal_templates
ORDER BY usage_count DESC;

-- Casos ativos por cliente
CREATE VIEW vw_active_cases AS
SELECT 
    c.id,
    c.case_number,
    c.case_type,
    c.state,
    cust.name as customer_name,
    c.created_at
FROM cases c
JOIN customers cust ON c.customer_id = cust.id
WHERE c.closed_at IS NULL
ORDER BY c.created_at DESC;
```

## 🔧 Índices Estratégicos

```sql
-- Customers
CREATE INDEX idx_customers_document ON customers(document);
CREATE INDEX idx_customers_type ON customers(type);

-- Cases
CREATE INDEX idx_cases_customer ON cases(customer_id);
CREATE INDEX idx_cases_state ON cases(state);
CREATE INDEX idx_cases_type ON cases(case_type);

-- Legal Templates
CREATE INDEX idx_templates_type ON legal_templates(template_type);
CREATE INDEX idx_templates_active ON legal_templates(is_active);

-- Knowledge Chunks (CRÍTICO para performance RAG)
CREATE INDEX idx_chunks_topic ON knowledge_chunks(topic);
CREATE INDEX idx_chunks_tags ON knowledge_chunks(tags);
CREATE INDEX idx_chunks_source ON knowledge_chunks(source_type, source_id);
CREATE INDEX idx_chunks_hash ON knowledge_chunks(chunk_hash);
CREATE INDEX idx_chunks_relevance ON knowledge_chunks(relevance_score DESC);
CREATE INDEX idx_chunks_usage ON knowledge_chunks(usage_count DESC);
CREATE INDEX idx_chunks_last_used ON knowledge_chunks(last_used_at);
```

## 🚀 Fluxo de Uso

### 1. Indexação de Conhecimento
```python
# Ao adicionar novo documento jurídico:
# 1. Dividir em chunks
# 2. Calcular hash de cada chunk
# 3. Verificar se já existe (deduplicação)
# 4. Salvar com topic/tags extraídos
# 5. Inicializar contadores (usage=0, success=0, fail=0)
```

### 2. Recuperação RAG com Ranking
```python
# Ao gerar petição:
# 1. Extrair topic/tags da query do usuário
# 2. Buscar chunks com MATCH de topic/tags
# 3. Ordenar por ranking_score (calculado dinamicamente)
# 4. Retornar top-N chunks mais relevantes
# 5. Incrementar usage_count dos chunks retornados
```

### 3. Feedback de Relevância
```python
# Após o usuário revisar a petição gerada:
# - Se chunk foi útil: success_count++
# - Se chunk foi rejeitado: fail_count++
# - Recalcular relevance_score periodicamente
```

### 4. Uso de Templates pelo LLM
```python
# Para gerar petição:
# 1. Selecionar template pelo tipo (ex: "habeas_corpus")
# 2. Carregar structure_json e variables_schema
# 3. Preencher variáveis com dados do caso
# 4. Buscar jurisprudência relevante via RAG
# 5. LLM gera petição final combinando tudo
# 6. Incrementar usage_count do template
# 7. NÃO salvar petição gerada no DB (apenas entregar ao usuário)
```

## 🛡️ Segurança e LGPD

- Dados sensíveis de clientes criptografados em repouso
- Audit trail de todas as operações críticas
- Controle de acesso por nível de permissão
- Anonimização de dados em logs e exports
- Retenção configurável de dados inativos

## 📈 Roadmap

### Fase 1 (Atual)
- ✅ Schema básico das 4 tabelas
- ✅ Sistema de ranking inteligente
- ✅ Templates para LLM
- ✅ Deduplicação por hash

### Fase 2 (Próxima)
- [ ] Full-text search nativo do SQLite
- [ ] API de feedback de relevância
- [ ] Dashboard de estatísticas
- [ ] Export/import de templates

### Fase 3 (Futura)
- [ ] Versionamento automático de templates
- [ ] A/B testing de chunks
- [ ] Integração com APIs jurídicas (STF/STJ)
- [ ] Cache distribuído

## 📁 Localização dos Arquivos

- **Schema SQL**: `/workspace/JURIDICO/schema.sql`
- **Plano Completo**: `/workspace/JURIDICO/DB_PLAN.md`
- **Templates Originais**: `/workspace/minutas-*` (arquivos fonte)
- **Banco de Dados**: `/workspace/JURIDICO/juridico.db` (após criação)
