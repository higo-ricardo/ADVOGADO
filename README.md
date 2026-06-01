# Agente Jurídico

App Streamlit para geração de peças processuais com IA, usando OpenRouter (modelos gratuitos) + RAG semântico local.

## Estrutura do projeto

```
C:\Users\hig0\Desktop\HIGO\ADVOGADO
├── app.py
├── state.py
├── router.py
├── knowledge.py
├── agent.py
├── rag.py
├── text_utils.py
├── export.py
├── requirements.txt
├── .streamlit/
│   ├── secrets.toml
│   └── config.toml
├── ui/
│   ├── components.py
│   └── pages.py
├── knowledge/
│   ├── README.md
│   ├── roteamento.md
│   ├── minuta-base.md
│   ├── contrato_decisao.md
│   ├── advogado.md
│   ├── estagiario.md
│   ├── estilo_juridico.md
│   ├── task.md
│   ├── imobiliarias/
│   │   ├── acao_imissao_posse.md
│   │   ├── acao_interdito_proibitorio.md
│   │   ├── acao_manutencao_posse.md
│   │   ├── acao_reintegracao_posse.md
│   │   ├── acao_reivindicatoria.md
│   │   ├── contestacao_usucapiao.md
│   │   ├── vizinhanca_direito_construir.md
│   │   ├── acao_anulatoria_documento.md
│   │   ├── acao_passagem_forcada.md
│   │   └── acao_demarcacao_terras.md
│   ├── civeis/
│   │   ├── cobranca_alugueis_rescisao.md
│   │   ├── distrato_recusa_demora.md
│   │   └── replica_contestacao.md
│   ├── intermediarias/
│   │   ├── procuracao_ad_judicia.md
│   │   ├── expedicao_alvara.md
│   │   ├── cumprimento_sentenca.md
│   │   ├── substabelecimento.md
│   │   ├── habilitacao_advogado.md
│   │   ├── declaracao_hipossuficiencia.md
│   │   └── peticao_acordo.md
│   ├── familia/
│   │   ├── nep.md
│   │   ├── inp.md
│   │   ├── ali.md
│   │   ├── exa.md
│   │   ├── inv.md
│   │   ├── ofa.md
│   │   ├── une.md
│   │   ├── int.md
│   │   ├── gua.md
│   │   ├── vis.md
│   │   ├── cur.md
│   │   └── div.md
│   ├── remedios-constitucionais.md
│   ├── recursos-civeis.md
│   ├── fontes.md
│   ├── verbetesSTF.md
│   ├── verbetesSTJ.md
│   └── sumulas-vinculantes.md
└── docs/
    ├── CHANGELOG.md
    ├── ROADMAP.md
    └── BACKLOG.md
```

## Tecnologias principais

- Streamlit (interface)
- OpenRouter (modelos gratuitos com fallback automático)
- RAG local com `sentence-transformers` + FAISS
- Python 3.14

## Como rodar

```bash
streamlit run app.py
```

## Configuração

- API key em `.streamlit/secrets.toml` (`OPENROUTER_API_KEY`)
- Modelo primário configurado em `agent.py`: `openrouter/free`

## Documentação

- `docs/ROADMAP.md` — melhorias planejadas
- `docs/BACKLOG.md` — pendências técnicas
- `docs/CHANGELOG.md` — histórico de alterações
