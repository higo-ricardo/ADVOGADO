# Changelog

## [NÃO VERSIONADO] — 2026-06-01
- Implementado RAG com embeddings locais (`all-MiniLM-L6-v2`) + FAISS
- Divididas as minutas em pastas por domínio (`imobiliarias/`, `civeis/`, `familia/`, `intermediarias/`)
- Adicionada subseção obrigatória de dispensa de audiência de conciliação em todas as peças compatíveis
- Configurado roteamento automático de modelos gratuitos OpenRouter (`openrouter/free` + fallbacks)
- Removidos emojis do código fonte para evitar conflito de encoding no Windows
- Criados `text_utils.py`, `rag.py` e ajustado `agent.py` para normalização UTF-8
- Criados `docs/CHANGELOG.md`, `docs/ROADMAP.md` e `docs/BACKLOG.md`
