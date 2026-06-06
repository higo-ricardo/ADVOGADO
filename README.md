# Agente Jurídico

App Streamlit para geração de peças processuais com IA, usando OpenRouter (modelos gratuitos) + RAG semântico local.

## ✨ Novidades

- **Tema escuro/claro** - Toggle na sidebar para alternância de tema visual
- **Importação de templates** - Faça upload de templates personalizados (.docx, .txt, .md)
- **Importação de estilo jurídico** - Personalize o estilo de redação (.txt, .md)
- **Interface jurídica profissional** - Paleta de cores sofisticada e componentes modernos

## Estrutura do projeto

```
ADVOGADO/
├── app.py                          # Entry point
├── core/
│   ├── state_machine.py           # Máquina de estados testável
│   ├── router.py                  # Roteamento de domínios
│   └── contract.py                # Lógica de contrato
├── ui/
│   ├── components.py              # Componentes reutilizáveis (cards, badges, uploaders)
│   └── pages.py                   # 6 telas do fluxo
├── services/
│   ├── llm/                       # Providers de LLM
│   ├── rag/                       # Indexação e recuperação semântica
│   ├── knowledge/                 # Base de conhecimento
│   └── document.py                # Geração de documentos
├── infrastructure/                 # Config, logging, exceções
├── knowledge/                      # Minutas e fontes jurídicas
├── data/
│   └── templates/                  # Templates personalizados (upload)
│   └── estilos/                    # Estilos personalizados (upload)
├── .streamlit/
│   ├── secrets.toml               # API keys
│   └── config.toml                # Configurações do Streamlit
└── docs/                          # Documentação
```

## Tecnologias

- **Streamlit** - Interface web reativa
- **OpenRouter** - Modelos LLM gratuitos com fallback
- **Sentence-transformers** - Embeddings para RAG
- **python-docx** - Exportação para Word

## Como rodar

```bash
streamlit run app.py
```

## Configuração

1. Configure a API key em `.streamlit/secrets.toml`:
```toml
OPENROUTER_API_KEY = "sua_chave_aqui"
```

2. Opcional: instale `python-docx` para exportar peças em .docx:
```bash
pip install python-docx
```

## Funcionalidades

- **Etapas do fluxo**: Triagem → Confirmação → Coleta → Contrato → Geração → Revisão
- **Upload de templates**: Adicione templates personalizados via sidebar
- **Upload de estilo**: Personalize padrões de formatação jurídica
- **Tema escuro**: Ative para reduzir fadiga visual
- **Exportação**: Download em .txt (sempre) e .docx (com python-docx)

## Documentação

- `docs/ROADMAP.md` — Melhorias planejadas
- `docs/BACKLOG.md` — Pendências técnicas
- `docs/CHANGELOG.md` — Histórico de alterações