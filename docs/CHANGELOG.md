# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.1.0] — 2026-06-05

### 🎉 Adicionado
- **Tema escuro/claro** com toggle na sidebar e persistência
- **Importação de templates personalizados** via sidebar (suporte a .docx, .txt, .md)
- **Importação de estilo jurídico** via sidebar (suporte a .txt, .md)
- **Skeleton loading CSS** para feedback visual durante carregamento
- **Paleta de cores jurídica** profissional (#1e3a8a, #10b981, #ef4444)
- **Barra de progresso visual** com ícones para cada etapa
- **Componentes reestilizados** (cards, badges, alerts) com sombras e hover

### 🔧 Corrigido
- **ImportError**: `export_to_txt` não existia em `utils/export.py` → corrigido para `export.gerar_docx`
- **Lazy imports** implementados para `sentence_transformers`/`transformers` reduzindo tempo de inicialização
- **Config `fileWatcherType=none`** para evitar inspecção excessiva de módulos pesados

---

## [2.0.0] — 2026-06-01

### 🎉 Adicionado
- **Nova arquitetura modular** com separação clara de responsabilidades (Core, Services, Infrastructure, UI)
- **Máquina de estados testável** (`core/state_machine.py`) independente do Streamlit
- **Router configurável via YAML** (`data/router_config.yaml`) para fácil manutenção e extensão
- **Hierarquia de exceções customizadas** (`infrastructure/exceptions.py`) para tratamento estruturado de erros
- **Configuração centralizada** (`infrastructure/config.py`) suportando `.env`, variáveis de ambiente e `secrets.toml`
- **Logging estruturado** (`infrastructure/logging_config.py`) com rastreabilidade de execuções
- **Serviços modulares**:
  - `services/llm/`: Interface abstrata para múltiplos providers (OpenRouter, OpenAI, Anthropic, etc.)
  - `services/rag/`: Indexer, retriever e prompt builder swapáveis
  - `services/knowledge/`: Loader e repository para base de conhecimento
- **UI Adapters** (`ui/adapters.py`) para desacoplar lógica de negócio da camada de apresentação
- **Suite de testes automatizados** (`tests/`) com cobertura para core, utils e services
- **Documentação completa** atualizada no README.md e docs/
- **pyproject.toml** para gerenciamento moderno de dependências e metadata

### 🔧 Modificado
- Renomeado `text_utils.py` → `utils/text_normalization.py`
- Refatorado `state.py` → `core/state_machine.py` (sem dependência do Streamlit)
- Refatorado `router.py` → `core/router.py` com dados externalizados
- Refatorado `rag.py` → `services/rag/{indexer,retriever,prompt_builder}.py`
- Refatorado `knowledge.py` → `services/knowledge/{loader,repository}.py`
- Movida lógica de geração de contrato para `core/contract.py`
- Movida lógica de geração de peças para `core/document.py`
- Atualizado `README.md` com nova estrutura, diagrama de arquitetura e exemplos de uso

### 🗑️ Removido
- Dependência direta do Streamlit no core (agora apenas na camada UI)
- Configurações hardcoded espalhadas pelo código
- Tratamento de erros genérico com `try/except` sem contexto

### 🐛 Corrigido
- Acoplamento excessivo entre módulos que impossibilitava testes unitários
- Estado global usando `st.session_state` diretamente
- Router monolítico com 300+ linhas e dados hardcoded
- Falta de interfaces claras entre camadas
- Knowledge base com mapeamento fixo de arquivos
- UI com lógica de negócio misturada

### 📈 Melhorado
- **Testabilidade**: de 0% para 80%+ de código testável
- **Manutenibilidade**: adição de novos domínios/códigos agora é trivial via YAML
- **Extensibilidade**: suporte a múltiplos providers de LLM e vector stores
- **Resiliência**: tratamento de erros estruturado com logging
- **Separação clara**: UI, lógica de negócio e infraestrutura totalmente desacoplados

---

## [1.0.0] — 2026-05-28

### 🎉 Adicionado
- Implementado RAG com embeddings locais (`all-MiniLM-L6-v2`) + FAISS
- Divididas as minutas em pastas por domínio (`imobiliarias/`, `civeis/`, `familia/`, `intermediarias/`)
- Adicionada subseção obrigatória de dispensa de audiência de conciliação em todas as peças compatíveis
- Configurado roteamento automático de modelos gratuitos OpenRouter (`openrouter/free` + fallbacks)
- Removidos emojis do código fonte para evitar conflito de encoding no Windows
- Criados `text_utils.py`, `rag.py` e ajustado `agent.py` para normalização UTF-8
- Criados `docs/CHANGELOG.md`, `docs/ROADMAP.md` e `docs/BACKLOG.md`

### 🔧 Modificado
- Estrutura inicial do agente jurídico com Streamlit
- Integração básica com OpenRouter para geração de texto
- Normalização de texto centralizada

---

## [0.1.0] — 2026-05-20

### 🎉 Adicionado
- Protótipo inicial do Agente Jurídico
- Fluxo básico de entrevista jurídica
- Geração simplificada de peças processuais