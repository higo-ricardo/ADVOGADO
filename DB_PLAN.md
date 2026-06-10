# Plano de Banco de Dados - Agente Jurídico IA

## 1. Visão Geral do Sistema

### 1.1 Propósito
Sistema de gerenciamento jurídico com IA para automação de peças processuais, gestão de casos e suporte à decisão baseado em jurisprudência (STF/STJ).

### 1.2 Filosofia do Design
- **Minimalismo**: Apenas o necessário, zero complexidade desnecessária
- **SQLite Nativo**: Aproveitar recursos nativos sem forçar padrões de bancos grandes
- **Metadados Inteligentes**: Busca contextual via tags/tópicos ao invés de embeddings
- **Manutenção Zero**: Triggers e defaults automatizam tudo

### 1.3 Tecnologia
- **SGBD**: SQLite >= 3.35.0
- **Modo**: WAL (Write-Ahead Logging)
- **Linguagem**: Python 3.10+
- **Padrão Arquitetural**: Repository Pattern

---

## 2. Modelo de Dados Simplificado

### 2.1 Diagrama Entidade-Relacionamento

```
┌─────────────┐       ┌─────────────┐       ┌──────────────┐
│  customers  │───┬──▶│    cases    │───┬──▶│ case_states  │
└─────────────┘   │   └─────────────┘   │   └──────────────┘
                  │                     │
                  │                     ├──▶│  documentos   │
                  │                     │   └──────────────┘
                  │                     │
┌─────────────┐   │   ┌───────────────┐ │   
│ knowledge   │───┼──▶│  juris_cache  │◀──┘   
└─────────────┘   │   └───────────────┘     
                  │                         
┌─────────────┐   │                         
│  auditlog   │◀──┘                         
└─────────────┘                             
```

**Mudança Chave**: Unificamos `fontes_url`, `verbetes_stf`, `verbetes_stj` e `knowledge_cache` em apenas **2 tabelas**:
- `knowledge`: Fontes originais (URLs, leis, súmulas)
- `juris_cache`: Chunks já processados com metadados ricos

---

## 3. Esquema de Tabelas

### 3.1 Tabela: `customers`

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| id | INTEGER | NO | AUTOINCREMENT | Chave primária |
| type | TEXT | NO | PF | Tipo: PF ou PJ |
| name | TEXT | NO | - | Nome completo |
| document | TEXT | NO | - | CPF/CNPJ |
| email | TEXT | YES | NULL | E-mail |
| phone | TEXT | YES | NULL | Telefone |
| metadata | JSON | YES | NULL | Dados extras |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | Criação |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | Atualização |
| is_active | BOOLEAN | NO | TRUE | Status |

**Repository**: `CustomerRepository`

---

### 3.2 Tabela: `cases`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| customer_id | INTEGER | FK → customers.id |
| case_number | TEXT | Número do processo |
| court | TEXT | Tribunal/Vara |
| status | TEXT | ATIVO/SUSPENSO/ARQUIVADO/ENCERRADO |
| subject | TEXT | Assunto |
| description | TEXT | Descrição |
| metadata | JSON | Dados extras |
| created_at | TIMESTAMP | Criação |
| updated_at | TIMESTAMP | Atualização |

**Repository**: `CaseRepository`

---

### 3.3 Tabela: `case_states`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| case_id | INTEGER | FK → cases.id |
| state_name | TEXT | Estado atual |
| context_data | JSON | Snapshot do contexto |
| transition_reason | TEXT | Motivo da transição |
| created_at | TIMESTAMP | Data |

**Repository**: Integrado ao `CaseRepository`

---

### 3.4 Tabela: `documentos`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| case_id | INTEGER | FK → cases.id |
| document_type | TEXT | Tipo da peça |
| title | TEXT | Título |
| content | TEXT | Conteúdo |
| version | INTEGER | Versão |
| is_latest | BOOLEAN | É a mais recente? |
| created_at | TIMESTAMP | Data |
| author_ai_model | TEXT | Modelo IA |

**Triggers**: `trg_documentos_invalidate_old`

**Repository**: `DocumentRepository`

---

### 3.5 Tabela: `knowledge` ⭐ UNIFICADA

Fontes de conhecimento unificadas (URLs, súmulas STF/STJ, leis, doutrinas).

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| source_type | TEXT | url/stf_sumula/stj_sumula/lei/doutrina |
| title | TEXT | Título descritivo |
| url | TEXT | URL de origem |
| content | TEXT | Conteúdo completo (opcional) |
| content_hash | TEXT | Hash SHA256 único |
| topic | TEXT | Tópico principal |
| tags | TEXT | Tags (vírgula-separadas) |
| metadata | JSON | Metadados específicos |
| is_active | BOOLEAN | Fonte ativa |
| created_at | TIMESTAMP | Data |

**Índices**: `idx_knowledge_type`, `idx_knowledge_topic`, `idx_knowledge_tags`, `idx_knowledge_hash`

**Repository**: `KnowledgeRepository`

---

### 3.6 Tabela: `juris_cache` ⭐ SISTEMA DE RANKING INTELIGENTE

Cache de chunks com **sistema de ranking multi-fator** para RAG preciso.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| knowledge_id | INTEGER | FK → knowledge.id |
| chunk_order | INTEGER | Ordem no documento |
| content | TEXT | Texto do chunk (~800 chars) |
| topic | TEXT | Tópico principal |
| tags | TEXT | Tags específicas |
| base_quality | INTEGER | Qualidade intrínseca (0-100, default 50) |
| usage_count | INTEGER | Total de usos |
| success_count | INTEGER | Usos com feedback positivo |
| failure_count | INTEGER | Usos com feedback negativo |
| recency_boost | INTEGER | Bônus por recente (0-20) |
| context_relevance | INTEGER | Relevância contextual (0-100) |
| last_used_at | TIMESTAMP | Último uso |
| created_at | TIMESTAMP | Data criação |

**Índices**: 
- `idx_juris_cache_topic` (**principal para RAG**)
- `idx_juris_cache_tags`
- `idx_juris_cache_ranking` (composite: topic, calculated_score DESC)
- `idx_juris_cache_recency`

**Fórmula de Ranking Dinâmico**:
```sql
-- Score calculado em tempo real (0-100+)
SELECT 
    id, content, topic,
    -- Fórmula de ranking multi-fator
    (
        base_quality * 0.4 +                          -- 40% qualidade base
        COALESCE(success_rate, 0) * 100 * 0.3 +       -- 30% taxa de sucesso
        recency_boost * 0.2 +                         -- 20% recenticidade
        context_relevance * 0.1                       -- 10% relevância contextual
    ) AS calculated_score,
    usage_count,
    success_count,
    failure_count
FROM juris_cache
CROSS JOIN (
    SELECT 
        CAST(success_count AS FLOAT) / NULLIF(usage_count, 0) AS success_rate
    FROM juris_cache
) AS rates
WHERE topic = ?
ORDER BY calculated_score DESC
LIMIT 5;
```

**Fluxo Completo**:
```python
# Indexação inicial
INSERT INTO juris_cache (
    knowledge_id, chunk_order, content, topic, tags, 
    base_quality, context_relevance
) VALUES (?, ?, ?, ?, ?, 50, 50);

# Recuperação RAG com ranking inteligente
SELECT content, calculated_score 
FROM juris_cache 
WHERE topic = ? 
  AND tags LIKE '%?%'
ORDER BY calculated_score DESC 
LIMIT 5;

# Feedback POSITIVO (peça foi útil)
UPDATE juris_cache 
SET 
    usage_count = usage_count + 1,
    success_count = success_count + 1,
    recency_boost = MIN(recency_boost + 5, 20),  -- Boost até 20
    context_relevance = MIN(context_relevance + 3, 100),
    last_used_at = CURRENT_TIMESTAMP 
WHERE id = ?;

# Feedback NEGATIVO (peça não serviu)
UPDATE juris_cache 
SET 
    usage_count = usage_count + 1,
    failure_count = failure_count + 1,
    recency_boost = MAX(recency_boost - 5, 0),   -- Penaliza recente
    context_relevance = MAX(context_relevance - 5, 0)
WHERE id = ?;

# Decaimento temporal (executar semanalmente)
-- Reduz recency_boost gradualmente para chunks antigos
UPDATE juris_cache 
SET recency_boost = MAX(recency_boost - 2, 0)
WHERE last_used_at < datetime('now', '-7 days');

# Limpeza inteligente
DELETE FROM juris_cache
WHERE 
    usage_count > 0 
    AND success_count * 1.0 / usage_count < 0.2  -- <20% sucesso
    AND created_at < datetime('now', '-60 days');
```

**Métricas de Qualidade**:
```sql
-- View de estatísticas por chunk
CREATE VIEW vw_chunk_performance AS
SELECT 
    id,
    topic,
    usage_count,
    success_count,
    failure_count,
    ROUND(success_count * 100.0 / NULLIF(usage_count, 0), 2) AS success_rate_pct,
    base_quality,
    recency_boost,
    context_relevance,
    last_used_at,
    CASE 
        WHEN usage_count = 0 THEN 'NOVO'
        WHEN success_count * 1.0 / usage_count >= 0.8 THEN 'EXCELENTE'
        WHEN success_count * 1.0 / usage_count >= 0.6 THEN 'BOM'
        WHEN success_count * 1.0 / usage_count >= 0.4 THEN 'REGULAR'
        ELSE 'RUIM'
    END AS performance_tier
FROM juris_cache;
```

**Vantagens do Sistema de Ranking**:
- ✅ **Multi-fator**: Combina qualidade, sucesso, recenticidade e contexto
- ✅ **Auto-aprendizado**: Melhora com o uso real (feedback loop)
- ✅ **Decaimento temporal**:Chunks antigos perdem boost naturalmente
- ✅ **Feedback binário simples**: Sucesso/falha fácil de implementar
- ✅ **Performance tiers**: Classificação automática (Excelente/Bom/Regular/Ruim)
- ✅ **Limpeza baseada em métricas**: Remove apenas os realmente ruins
- ✅ **Zero embeddings**: Tudo com SQL puro e metadados

**Repository**: `KnowledgeRepository`

---

### 3.7 Tabela: `auditlog`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| table_name | TEXT | Tabela afetada |
| operation | TEXT | INSERT/UPDATE/DELETE |
| record_id | INTEGER | ID do registro |
| old_values | JSON | Valores antigos |
| new_values | JSON | Novos valores |
| changed_by | TEXT | Usuário |
| changed_at | TIMESTAMP | Data |

**Triggers**: Auditoria automática em customers/cases

**Repository**: `AuditLogRepository`

---

### 3.8 Tabela: `system_logs`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| log_level | TEXT | DEBUG/INFO/WARN/ERROR |
| message | TEXT | Mensagem |
| case_id | INTEGER | FK opcional |
| details | JSON | Detalhes |
| created_at | TIMESTAMP | Data |

---

## 4. Views

- `vw_customer_history`: Histórico por cliente
- `vw_audit_cases`: Auditoria de casos
- `vw_recent_changes`: Mudanças (24h)
- `vw_case_timeline`: Linha do tempo
- `vw_knowledge_stats`: Stats de conhecimento

---

## 5. Repositórios

| Repositório | Entidades |
|-------------|-----------|
| CustomerRepository | customers |
| CaseRepository | cases, case_states |
| DocumentRepository | documentos |
| KnowledgeRepository | knowledge, juris_cache |
| AuditLogRepository | auditlog |

---

## 6. Exemplo RAG

```python
from data.repositories.knowledge_repository import KnowledgeRepository

repo = KnowledgeRepository()

# Busca chunks
chunks = repo.search_chunks(
    topic="habeas corpus",
    tags="prisão ilegal",
    limit=5
)

# Feedback
repo.mark_as_used(chunks[0]['id'])
```

---

## 7. Roadmap

**Fase 1** (Atual):
- ✅ 8 tabelas simplificadas
- ✅ juris_cache com metadados
- ✅ Zero embeddings

**Fase 2** (Opcional):
- [ ] FTS5 full-text search
- [ ] Auto-adjust quality_score

**Fase 3** (Futuro):
- [ ] Replicação leitura
- [ ] Particionamento

---

## 8. Resumo Melhorias

| Item | Antes | Agora | Benefício |
|------|-------|-------|-----------|
| Tabelas conhecimento | 4 | 2 | -50% complexidade |
| Busca RAG | Embeddings | Metadados + Ranking | Zero ML + Inteligente |
| Contador de usos | Único | Sucesso/Falha/Recência | Feedback rico |
| Sistema de ranking | Estático | Multi-fator dinâmico | Auto-aprendizado |
| Limpeza | Baseada em tempo | Baseada em métricas | Remove só os ruins |
| Debug | Complexo | SQL puro + Views | Produtividade |

**Fórmula de Ranking**:
```
calculated_score = 
    (base_quality × 40%) +
    (success_rate × 100 × 30%) +
    (recency_boost × 20%) +
    (context_relevance × 10%)
```

**Exemplo Prático**:
- Chunk A: quality=80, success=90%, recency=15, relevance=70 → **Score: 83.5**
- Chunk B: quality=60, success=50%, recency=5, relevance=50 → **Score: 50.0**
- Chunk C: quality=90, success=20%, recency=0, relevance=40 → **Score: 50.0** (falha muito!)

Resultado: Chunk A é priorizado, mesmo tendo qualidade base menor que C.

---

**Status**: ⏳ Aguardando aprovação

**Próximos passos**:
1. Aprovar plano
2. Gerar schema.sql
3. Implementar repositórios
4. Testar fluxos
