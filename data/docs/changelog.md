# Changelog - Database Agente Jurídico IA

Todas as mudanças significativas no schema e estrutura do banco de dados serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e segue [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Não Lançado] - v1.1.0 (Em Desenvolvimento)

### Adicionado
- Tabela `auditlog` para rastreabilidade completa de operações
- Views de auditoria: `vw_audit_cases`, `vw_audit_documents`, `vw_customer_history`
- Triggers automáticas para captura de mudanças em tabelas críticas
- Coluna `updated_by` em tabelas principais para auditoria de usuário

### Modificado
- Política de retenção de logs implementada
- Otimização de índices para queries de auditoria

### Segurança
- Implementação de masking para dados sensíveis em logs
- Controle de acesso por nível de permissão

---

## [1.0.0] - 2024-XX-XX - Lançamento Inicial

### Adicionado

#### Tabelas Principais (8)

1. **`customers`**
   - Gestão de clientes (pessoas físicas e jurídicas)
   - Campos: id, type, name, document, email, phone, address, created_at, updated_at
   - Constraints: UK_document (CPF/CNPJ único)

2. **`cases`**
   - Registro de casos jurídicos
   - Campos: id, customer_id, case_number, court, class, status, subject, created_at, updated_at
   - Constraints: FK_customer_id, UK_case_number

3. **`case_states`**
   - Versionamento de estados de casos
   - Campos: id, case_id, status, description, changed_at, changed_by, reason
   - Constraints: FK_case_id

4. **`documentos`**
   - Armazenamento de documentos com versionamento
   - Campos: id, case_id, version, doc_type, title, content_hash, file_path, metadata, created_at, created_by
   - Constraints: FK_case_id, UK_case_version (case_id + version)

5. **`verbetes_stf`**
   - Jurisprudências do Supremo Tribunal Federal
   - Campos: id, source_url_id, theme, summary, device, rapporteur, judgment_date, publish_date, metadata, created_at
   - Constraints: FK_source_url_id

6. **`verbetes_stj`**
   - Jurisprudências do Superior Tribunal de Justiça
   - Campos: id, source_url_id, theme, summary, device, rapporteur, judgment_date, publish_date, metadata, created_at
   - Constraints: FK_source_url_id

7. **`fontes_url`**
   - Fontes originais de jurisprudências
   - Campos: id, url, source_type, content_hash, last_verified, is_valid, created_at
   - Constraints: UK_url

8. **`knowledge_cache`**
   - Cache de chunks de conhecimento para RAG
   - Campos: id, source_type, source_id, chunk_hash, content, metadata, embedding, ttl, created_at, expires_at
   - Constraints: UK_chunk_hash

9. **`system_logs`**
   - Logs estruturados do sistema
   - Campos: id, level, message, context, performance_ms, created_at
   - Índices: idx_level, idx_created_at

#### Índices
- `idx_customers_document` - Busca por CPF/CNPJ
- `idx_cases_customer_status` - Casos por cliente e status
- `idx_cases_number` - Busca por número processual
- `idx_case_states_case` - Histórico por caso
- `idx_documentos_case_version` - Documentos por caso e versão
- `idx_verbetes_stf_theme` - Busca por tema STF
- `idx_verbetes_stj_theme` - Busca por tema STJ
- `idx_fontes_url_hash` - Verificação de integridade
- `idx_knowledge_cache_source` - Cache por origem
- `idx_system_logs_level_date` - Logs filtrados

#### Constraints
- Chaves estrangeiras com `ON DELETE CASCADE`
- Unique constraints para identificadores naturais
- Check constraints para validação de dados
- Default values para timestamps

#### Relacionamentos
```
customers (1) ──< (N) cases
cases (1) ──< (N) case_states
cases (1) ──< (N) documentos
fontes_url (1) ──< (N) verbetes_stf
fontes_url (1) ──< (N) verbetes_stj
```

### Documentação
- Guia completo de estruturação (`guia.md`)
- Backlog de desenvolvimento (`backlog.md`)
- Scripts de migração inicial

### Performance
- WAL mode habilitado para concorrência
- Índices otimizados para queries frequentes
- Prepared statements para operações CRUD

---

## [0.2.0] - 2024-XX-XX - Pré-lançamento

### Adicionado
- Estrutura inicial de repositórios
- Conexão básica com SQLite
- Schema preliminar (5 tabelas)

### Removido
- Dependência de `logging_config` externo
- Tabelas redundantes consolidadas

---

## [0.1.0] - 2024-XX-XX - Prova de Conceito

### Adicionado
- Primeiro protótipo de banco de dados
- Tabelas básicas: cases, documentos, logs
- Scripts de criação manual

### Observações
- Versão experimental não recomendada para produção
- Schema sujeito a mudanças significativas

---

## Versões Futuras (Planejamento)

### [1.2.0] - Otimização
- [ ] Índices full-text para buscas em ementas
- [ ] Índices parciais para dados ativos
- [ ] Scripts de manutenção automatizada
- [ ] Vacuum e analyze agendados

### [2.0.0] - Suporte Vetorial
- [ ] Coluna `embedding_vector` (BLOB) para busca semântica
- [ ] Integração com sqlite-vss ou similar
- [ ] API de similaridade de documentos
- [ ] Migração de knowledge_cache para formato vetorial

### [2.1.0] - Alta Disponibilidade
- [ ] Estratégia de backup automatizado
- [ ] Point-in-time recovery
- [ ] Replicação em tempo real
- [ ] Monitoramento de integridade

---

## Políticas

### Versionamento
- **MAJOR**: Mudanças incompatíveis no schema
- **MINOR**: Novas tabelas/colunas compatíveis
- **PATCH**: Correções de bugs, índices, otimizações

### Compatibilidade Retroativa
- Versões minor mantêm compatibilidade com dados existentes
- Migrações automáticas quando possível
- Breaking changes apenas em versões major com guia de migração

### Depreciação
- Colunas/tabelas depreciadas mantidas por 2 versões minor
- Avisos de depreciação nos logs
- Documentação atualizada com alternativas

---

## Autores

- Equipe de Desenvolvimento - Agente Jurídico IA

## Contribuidores

- Lista de contribuidores do projeto

---

*Última atualização: 2024*
