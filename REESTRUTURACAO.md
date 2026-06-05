# Plano de Reestruturação do Agente Jurídico

## Status da Implementação

### ✅ Fase 1: Fundação (COMPLETA)

- [x] `infrastructure/__init__.py` — Pacote infrastructure criado
- [x] `infrastructure/exceptions.py` — Hierarquia de exceções
- [x] `infrastructure/config.py` — Configuração centralizada
- [x] `infrastructure/logging_config.py` — Logging estruturado
- [x] `utils/__init__.py` — Pacote utils criado
- [x] `utils/text_normalization.py` — Normalização de texto (renomeado de text_utils.py)
- [x] `utils/export.py` — Exportação DOCX (movido de export.py)
- [x] `.env.example` — Template de variáveis de ambiente
- [x] `.gitignore` — Atualizado com novos paths
- [x] `data/router_config.yaml` — Configuração externalizada do router
- [x] `core/__init__.py` — Pacote core criado
- [x] `core/state_machine.py` — State machine testável
- [x] `core/router.py` — Router baseado em configuração YAML

### 🔄 Fase 2: Services (EM ANDAMENTO)

Próximos passos:
- [ ] `services/llm/base.py` — Interface abstracta para LLM
- [ ] `services/llm/openrouter.py` — Implementação OpenRouter
- [ ] `services/llm/factory.py` — Factory para providers
- [ ] `services/rag/indexer.py` — Indexação de documentos
- [ ] `services/rag/retriever.py` — Busca semântica
- [ ] `services/rag/prompt_builder.py` — Construção de prompts
- [ ] `services/knowledge/loader.py` — Carregamento de arquivos .md
- [ ] `services/knowledge/repository.py` — Repositório de conhecimento

### ⏳ Fase 3: UI Adapter (PENDENTE)

- [ ] `ui/adapters.py` — Adaptadores UI ↔ Core
- [ ] Refatorar `ui/pages.py` para usar adapters
- [ ] Manter `app.py` mínimo apenas como bootstrap

### ⏳ Fase 4: Testes (PENDENTE)

- [ ] `tests/conftest.py` — Fixtures pytest
- [ ] Testes para `core/state_machine.py`
- [ ] Testes para `core/router.py`
- [ ] Testes para `services/rag/`
- [ ] Testes para `utils/text_normalization.py`

### ⏳ Fase 5: Migração e Cleanup (PENDENTE)

- [ ] Migrar imports no `app.py` para nova estrutura
- [ ] Manter compatibilidade retroativa com módulos antigos
- [ ] Documentar nova arquitetura no README
- [ ] Remover código legado após validação

---

## Nova Estrutura de Diretórios

```
/workspace
├── app.py                      # Entry point (Streamlit) - A ATUALIZAR
├── core/                       # ✅ Lógica de negócio pura
│   ├── __init__.py
│   ├── state_machine.py        # ✅ State machine testável
│   └── router.py               # ✅ Roteamento baseado em YAML
├── services/                   # 🔄 Serviços externos
│   ├── __init__.py
│   ├── llm/                    # Provedores LLM
│   ├── rag/                    # RAG
│   └── knowledge/              # Conhecimento
├── infrastructure/             # ✅ Infraestrutura
│   ├── __init__.py
│   ├── config.py               # ✅ Configuração
│   ├── logging_config.py       # ✅ Logging
│   └── exceptions.py           # ✅ Exceções
├── ui/                         # UI (Streamlit)
│   ├── __init__.py
│   ├── components.py           # Componentes visuais
│   ├── pages.py                # Telas do fluxo
│   └── adapters.py             # 🔄 A CRIAR
├── utils/                      # ✅ Utilitários
│   ├── __init__.py
│   ├── text_normalization.py   # ✅ Normalização
│   └── export.py               # ✅ Exportação
├── data/                       # ✅ Dados
│   ├── knowledge_index/        # Índice RAG (.gitignore)
│   ├── templates/              # Templates futuros
│   └── router_config.yaml      # ✅ Config do router
├── knowledge/                  # Base de conhecimento (mantida)
├── tests/                      # 🔄 Testes
│   └── __init__.py
├── docs/                       # Documentação (mantida)
├── .env.example                # ✅ Template env vars
├── .gitignore                  # ✅ Atualizado
└── REESTRUTURACAO.md           # ✅ Este arquivo
```

---

## Benefícios da Nova Arquitetura

| Antes | Depois |
|-------|--------|
| 0% testável | 80%+ testável |
| Acoplado ao Streamlit | Core independente |
| 1 provider LLM | Múltiplos providers (Strategy) |
| FAISS hardcoded | Vector store swapável |
| Configuração espalhada | Config centralizada |
| Sem logs | Logging estruturado |
| Router difícil de manter | Router baseado em config YAML |
| UI com lógica de negócio | UI apenas renderização |

---

## Próximos Passos Imediatos

1. **Implementar services/llm/** — Abstrair chamadas OpenRouter
2. **Implementar services/rag/** — Modularizar RAG
3. **Criar ui/adapters.py** — Desacoplar UI do Core
4. **Atualizar app.py** — Usar nova estrutura
5. **Adicionar testes** — Garantir qualidade

---

## Compatibilidade Retroativa

Durante a migração, os módulos antigos são mantidos:
- `state.py` → Usado até `app.py` ser migrado
- `router.py` → Usado até imports serem atualizados
- `agent.py` → Será refatorado na Fase 2
- `rag.py` → Será modularizado na Fase 2
- `knowledge.py` → Será movido para services/knowledge/
- `export.py` → Copiado para utils/export.py (manter legacy)
- `text_utils.py` → Copiado para utils/text_normalization.py (manter legacy)

---

## Como Contribuir

1. Escolha uma tarefa das fases acima
2. Crie branch feature/XXX
3. Implemente com testes
4. Submeta PR

---

*Documento gerado durante reestruturação — Última atualização: $(date +%Y-%m-%d)*
