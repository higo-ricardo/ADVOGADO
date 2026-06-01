# Roadmap — Agente Jurídico

## ✅ Já implantado
- [x] **1. RAG (Retrieval-Augmented Generation)** — busca semântica com embeddings locais (`all-MiniLM-L6-v2`) + FAISS; prompts usam apenas trechos relevantes da knowledge base, com economia de tokens e respostas mais precisas.

## 🔜 Próximas melhorias
- [ ] **2. Cache de geração por código+descrição** — evitar reconsultas idênticas ao modelo usando hash do contexto; reuso de peças geradas anteriormente.
- [ ] **3. Exportação em DOCX e PDF** — botão de download direto na tela de revisão (python-docx + weasyprint/reportlab).
- [ ] **4. Persistência de casos em SQLite** — histórico de casos e peças com busca por texto/domínio/data.
- [ ] **5. Seleção manual de modelo com comparação** — dropdown de modelos gratuitos + botão "Comparar modelos" lado a lado.
- [ ] **6. Modo escuro/claro e acessibilidade** — toggle de tema no Streamlit e melhorias de contraste/fonte.
- [ ] **7. Validação automática de campos obrigatórios** — bloquear geração de briefing até que todos os campos `*` estejam preenchidos.
- [ ] **8. Roteamento inteligente de domínio** — matching semântico no `router.py` usando os mesmos embeddings do RAG.
- [ ] **9. Logs estruturados e telemetria local** — registrar modelo, tempo, tokens, erros e ações do usuário em `logs/app.log`.
- [ ] **10. Templates de entrada pré-preenchidos** — exemplos de descrição de caso por domínio na etapa de triagem.
