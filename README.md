# Agente Jurídico — Setup

## Estrutura

```
advogado_agent/
├── app.py                  ← entry point
├── state.py                ← state machine (6 etapas)
├── router.py               ← roteamento determinístico (sem API)
├── knowledge.py            ← carrega .md da knowledge base
├── agent.py                ← chamadas à API Anthropic
├── export.py               ← exportação .docx / .txt
├── requirements.txt
├── .streamlit/
│   ├── secrets.toml        ← API key (não versionar)
│   └── config.toml         ← tema visual
├── ui/
│   ├── components.py       ← componentes reutilizáveis
│   └── pages.py            ← 6 telas do fluxo
└── knowledge/              ← copie os .md da skill aqui
    ├── advogado.md
    ├── estagiario.md
    ├── estilo_juridico.md
    ├── minuta-base.md
    ├── roteamento.md
    ├── minutas-imobiliarias.md
    ├── minutas-consumeristas.md
    ├── minutas-civeis.md
    ├── documentos.md
    ├── minutas-intermediariais.md
    ├── minutas-familia.md
    ├── remedios-constitucionais.md
    ├── recursos-civeis.md
    ├── fontes.md
    ├── verbetesSTF.md
    ├── verbetesSTJ.md
    └── sumulas-vinculantes.md
```

## Instalação local

```bash
# 1. Clone / copie o projeto
cd advogado_agent

# 2. Crie ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure a API key
# Edite .streamlit/secrets.toml e coloque sua chave:
# ANTHROPIC_API_KEY = "sk-ant-..."

# 5. Copie os arquivos .md da skill para knowledge/
cp /caminho/para/advogadov2_1/advogado/*.md knowledge/

# 6. Execute
streamlit run app.py
```

## Deploy no Streamlit Community Cloud (gratuito)

1. Suba o projeto para um repositório GitHub (privado)
2. **Não inclua** `.streamlit/secrets.toml` no repositório
3. Acesse https://share.streamlit.io → "New app"
4. Selecione o repositório e `app.py` como entry point
5. Em "Advanced settings → Secrets", cole:
   ```
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
6. Clique em Deploy

## Fluxo de uso (estagiário)

```
1. Descreva o caso livremente
   ↓
2. Confirme domínio e tipo de peça (pré-selecionado automaticamente)
   ↓
3. Preencha os campos obrigatórios do caso
   ↓
4. Revise o briefing gerado
   ↓
5. Acompanhe a geração da peça em tempo real
   ↓
6. Revise, solicite ajustes e baixe o .docx
```

## Adicionando novos campos obrigatórios

Edite `router.py` → dicionário `CAMPOS_OBRIGATORIOS`.
Cada campo tem: `id`, `label`, `tipo` (text | textarea | select) e opcionalmente `opcoes`.

## Adicionando novos códigos de peça

1. Adicione o código em `router.py` → `CODIGOS_POR_DOMINIO`
2. Adicione os campos em `router.py` → `CAMPOS_OBRIGATORIOS`
3. Adicione o mapeamento minuta em `knowledge.py` → `MINUTA_POR_CODIGO`
