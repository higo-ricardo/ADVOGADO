# Database Backlog - Agente Jurídico IA

## Visão Geral
Backlog de desenvolvimento e evolução do banco de dados SQLite para o sistema Agente Jurídico IA.

---

## Épicos

### EPIC-001: Infraestrutura Básica
- **ID**: DB-001
- **Título**: Criação do Schema Inicial
- **Descrição**: Implementar as 10 tabelas principais com constraints, índices e chaves estrangeiras.
- **Prioridade**: Crítica
- **Status**: ✅ Concluído
- **Versão**: v1.0.0

### EPIC-002: Gestão de Clientes e Casos
- **ID**: DB-002
- **Título**: Módulo Customers & Cases
- **Descrição**: Implementar repositórios para gestão de clientes e casos jurídicos com versionamento de estados.
- **Prioridade**: Alta
- **Status**: ✅ Concluído
- **Versão**: v1.0.0

### EPIC-003: Jurisprudência STF/STJ
- **ID**: DB-003
- **Título**: Base de Verbetes Especializada
- **Descrição**: Tabelas segregadas para verbetes do STF e STJ com metadados completos.
- **Prioridade**: Alta
- **Status**: ✅ Concluído
- **Versão**: v1.0.0

### EPIC-004: Auditoria e Logs
- **ID**: DB-004
- **Título**: Sistema de Audit Log
- **Descrição**: Implementar tabela auditlog para rastreabilidade completa de operações.
- **Prioridade**: Média
- **Status**: 🔄 Em Progresso
- **Versão**: v1.1.0

### EPIC-005: Otimização RAG
- **ID**: DB-005
- **Título**: Cache de Conhecimento Vetorial
- **Descrição**: Estruturar knowledge_cache para suporte a embeddings e busca semântica.
- **Prioridade**: Baixa
- **Status**: ⏳ Pendente
- **Versão**: v2.0.0

---

## Backlog Detalhado (User Stories)

### Sprint 1 - Fundação (v1.0.0)

#### US-001: Tabela Customers
- **Como** administrador do sistema
- **Quero** cadastrar e gerenciar clientes (pessoas físicas e jurídicas)
- **Para** vincular casos jurídicos a titulares específicos
- **Critérios de Aceite**:
  - [x] CPF/CNPJ único
  - [x] Suporte a PJ e PF
  - [x] Histórico de casos vinculados
  - [x] Dados de contato estruturados

#### US-002: Tabela Cases
- **Como** advogado
- **Quero** registrar casos jurídicos com número processual e tribunal
- **Para** organizar a base de processos
- **Critérios de Aceite**:
  - [x] Número do processo único
  - [x] Vínculo com customer
  - [x] Status do caso (ativo, arquivado, etc.)
  - [x] Metadados do tribunal

#### US-003: Tabela Case States
- **Como** sistema
- **Quero** versionar estados de casos
- **Para** permitir auditoria e rollback de situações
- **Critérios de Aceite**:
  - [x] Histórico completo de mudanças
  - [x] Timestamp de cada estado
  - [x] Motivo da mudança registrado

#### US-004: Tabela Documentos
- **Como** usuário
- **Quero** armazenar documentos com versionamento
- **Para** manter histórico de peças processuais
- **Critérios de Aceite**:
  - [x] Versionamento automático
  - [x] Hash de integridade
  - [x] Vínculo com caso
  - [x] Tipo de documento categorizado

#### US-005: Tabelas Verbetes STF/STJ
- **Como** advogado
- **Quero** consultar jurisprudências separadas por tribunal
- **Para** garantir precisão nas citações
- **Critérios de Aceite**:
  - [x] Tabelas segregadas STF/STJ
  - [x] Metadados completos (relator, data, tema)
  - [x] Busca por palavras-chave
  - [x] Ementa e dispositivo armazenados

#### US-006: Tabela Fontes URL
- **Como** pesquisador
- **Quero** registrar fontes originais de jurisprudências
- **Para** validar autenticidade das informações
- **Critérios de Aceite**:
  - [x] URL única
  - [x] Hash de conteúdo para detecção de mudanças
  - [x] Data de última verificação
  - [x] Status de validade

#### US-007: Tabela Knowledge Cache
- **Como** sistema de IA
- **Quero** armazenar chunks de conhecimento pré-processados
- **Para** otimizar respostas RAG
- **Critérios de Aceite**:
  - [x] Chunks identificados por hash
  - [x] Metadados de origem
  - [x] Suporte futuro a embeddings
  - [x] TTL para expiração

#### US-008: Tabela System Logs
- **Como** administrador
- **Quero** logs estruturados do sistema
- **Para** monitoramento e debugging
- **Critérios de Aceite**:
  - [x] Níveis de log (INFO, WARN, ERROR)
  - [x] Contexto da operação
  - [x] Performance metrics
  - [x] Rotação automática

---

### Sprint 2 - Auditoria (v1.1.0)

#### US-009: Tabela Audit Log
- **Como** compliance officer
- **Quero** rastrear todas as operações no banco
- **Para** conformidade com LGPD e auditorias
- **Critérios de Aceite**:
  - [ ] Tabela auditlog criada
  - [ ] Registro de INSERT, UPDATE, DELETE
  - [ ] Old values e new values armazenados
  - [ ] Usuário responsável registrado
  - [ ] Triggers automáticas em tabelas críticas

#### US-010: Views de Auditoria
- **Como** auditor
- **Quero** views consolidadas de alterações
- **Para** análise rápida de mudanças
- **Critérios de Aceite**:
  - [ ] View: vw_audit_cases
  - [ ] View: vw_audit_documents
  - [ ] View: vw_customer_history
  - [ ] View: vw_recent_changes

#### US-011: Triggers de Auditoria
- **Como** sistema
- **Quero** triggers automáticas em tabelas sensíveis
- **Para** garantir registro sem dependência de aplicação
- **Critérios de Aceite**:
  - [ ] Trigger: trg_audit_customers
  - [ ] Trigger: trg_audit_cases
  - [ ] Trigger: trg_audit_documentos
  - [ ] Trigger: trg_audit_verbetes

---

### Sprint 3 - Otimização (v1.2.0)

#### US-012: Índices Avançados
- **Como** DBA
- **Quero** índices compostos para queries frequentes
- **Para** melhorar performance de buscas
- **Critérios de Aceite**:
  - [ ] Índice composto: cases(customer_id, status)
  - [ ] Índice full-text: verbetes(ementa)
  - [ ] Índice parcial: documents(case_id WHERE active=1)

#### US-013: Procedures de Manutenção
- **Como** administrador
- **Quero** scripts de manutenção automatizada
- **Para** limpeza e otimização do banco
- **Critérios de Aceite**:
  - [ ] Script: vacuum_database.sql
  - [ ] Script: archive_old_cases.sql
  - [ ] Script: rotate_logs.sql
  - [ ] Script: verify_integrity.sql

---

### Sprint 4 - Evolução (v2.0.0)

#### US-014: Suporte Vetorial
- **Como** engenheiro de IA
- **Quero** armazenar embeddings de documentos
- **Para** busca semântica avançada
- **Critérios de Aceite**:
  - [ ] Coluna: embedding_vector (BLOB)
  - [ ] Integração com sqlite-vss
  - [ ] API de similaridade

#### US-015: Replicação e Backup
- **Como** DevOps
- **Quero** estratégia de backup automatizado
- **Para** recuperação de desastres
- **Critérios de Aceite**:
  - [ ] Backup diário automático
  - [ ] WAL mode configurado
  - [ ] Point-in-time recovery

---

## Métricas de Progresso

| Versão | Tarefas Totais | Concluídas | Em Progresso | Pendentes | % Concluído |
|--------|---------------|------------|--------------|-----------|-------------|
| v1.0.0 | 8             | 8          | 0            | 0         | 100%        |
| v1.1.0 | 3             | 0          | 1            | 2         | 10%         |
| v1.2.0 | 2             | 0          | 0            | 2         | 0%          |
| v2.0.0 | 2             | 0          | 0            | 2         | 0%          |
| **Total** | **15**     | **8**      | **1**        | **6**     | **60%**     |

---

## Dependências Técnicas

- SQLite >= 3.35.0 (suporte a generated columns)
- Python >= 3.10
- Bibliotecas: `aiosqlite`, `python-dateutil`
- Opcional: `sqlite-vss` para busca vetorial (v2.0.0)

---

## Riscos e Mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Crescimento excessivo da tabela auditlog | Alto | Médio | Política de retenção + archive mensal |
| Performance em buscas full-text | Médio | Baixo | Índices FTS5 + cache de resultados |
| Corrupção de banco em escrita concorrente | Alto | Baixo | WAL mode + transações adequadas |
| Vazamento de dados sensíveis | Crítico | Baixo | Criptografia de colunas sensíveis + acesso restrito |

---

*Última atualização: 2024*
*Responsável: Equipe de Desenvolvimento*
