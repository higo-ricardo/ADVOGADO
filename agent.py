"""
agent.py — Camada de chamadas via OpenRouter.
OpenRouter expõe API compatível com OpenAI; usa openai SDK apontando para
https://openrouter.ai/api/v1

Modelo padrão: anthropic/claude-sonnet-4-5
Troque MODEL para qualquer modelo disponível no OpenRouter.
"""
import json
from typing import Generator

import streamlit as st
from openai import OpenAI

from knowledge import (
    carregar_system_advogado,
    carregar_system_estagiario,
    contexto_completo_estagiario,
)

# ---------------------------------------------------------------------------
# Configuração — troque o modelo aqui se precisar
# Exemplos OpenRouter:
#   "anthropic/claude-sonnet-4-5"
#   "anthropic/claude-haiku-4-5"
#   "openai/gpt-4o"
#   "google/gemini-2.0-flash-001"
# ---------------------------------------------------------------------------
MODEL     = "anthropic/claude-sonnet-4-5"
MAX_TOKENS = 4096


@st.cache_resource(show_spinner=False)
def _client() -> OpenAI:
    api_key = st.secrets.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY não configurada em .streamlit/secrets.toml")
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            # Opcional mas recomendado pelo OpenRouter para identificar o app
            "HTTP-Referer": st.secrets.get("APP_URL", "http://localhost:8501"),
            "X-Title":      st.secrets.get("APP_NAME", "Agente Jurídico"),
        },
    )


def _montar_messages(system: str, historico: list[dict]) -> list[dict]:
    """Prepara lista de messages no formato OpenAI com system como primeiro item."""
    return [{"role": "system", "content": system}] + historico


# ---------------------------------------------------------------------------
# ADVOGADO — coleta de dados em loop de conversa
# ---------------------------------------------------------------------------

def advogado_turno(
    historico: list[dict],
    mensagem_usuario: str,
) -> Generator[str, None, None]:
    """
    Envia um turno para o orquestrador com streaming.
    Atualiza o histórico internamente.
    """
    system = carregar_system_advogado()
    historico.append({"role": "user", "content": mensagem_usuario})

    stream = _client().chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=_montar_messages(system, historico),
        stream=True,
    )

    resposta_completa = ""
    for chunk in stream:
        texto = chunk.choices[0].delta.content or ""
        resposta_completa += texto
        yield texto

    historico.append({"role": "assistant", "content": resposta_completa})


# ---------------------------------------------------------------------------
# CONTRATO — extração estruturada (sem streaming)
# ---------------------------------------------------------------------------

def gerar_contrato(
    descricao_caso: str,
    dominio: str,
    dominio_nome: str,
    codigo: str,
    codigo_nome: str,
    dados_coletados: dict,
    modo: str,
) -> dict:
    """
    Pede ao modelo o contrato_decisao como JSON puro.
    Retorna dict com os campos do contrato.
    """
    system = carregar_system_advogado()

    prompt = f"""
Com base nos dados abaixo, gere o contrato_decisao no formato JSON.
Responda SOMENTE com o JSON, sem texto adicional, sem markdown.

DADOS DO CASO:
- Descrição: {descricao_caso}
- Domínio: {dominio} — {dominio_nome}
- Código da peça: {codigo} — {codigo_nome}
- Modo: {modo}
- Dados coletados:
{json.dumps(dados_coletados, ensure_ascii=False, indent=2)}

CAMPOS OBRIGATÓRIOS DO JSON:
{{
  "escopo": "resumo dos fatos e tipo de peça",
  "tipo_peca": "{codigo} — {codigo_nome}",
  "dominio": "{dominio} — {dominio_nome}",
  "modo": "{modo}",
  "pedidos": ["pedido 1", "pedido 2"],
  "criterios_aceite": ["critério 1", "critério 2"],
  "regras_criticas": ["regra crítica específica do código {codigo}"],
  "dados": {json.dumps(dados_coletados, ensure_ascii=False)},
  "dependencias": ["fontes.md", "verbetesSTJ.md"],
  "observacoes": "observações adicionais do advogado"
}}
""".strip()

    resposta = _client().chat.completions.create(
        model=MODEL,
        max_tokens=2048,
        messages=_montar_messages(system, [{"role": "user", "content": prompt}]),
        stream=False,
    )

    texto = resposta.choices[0].message.content.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {
            "escopo": descricao_caso,
            "tipo_peca": f"{codigo} — {codigo_nome}",
            "dominio": f"{dominio} — {dominio_nome}",
            "modo": modo,
            "pedidos": ["[A PREENCHER]"],
            "criterios_aceite": ["Peça aderente aos fatos", "Todos os pedidos presentes"],
            "regras_criticas": [],
            "dados": dados_coletados,
            "dependencias": [],
            "observacoes": texto,
        }


# ---------------------------------------------------------------------------
# ESTAGIÁRIO — redação da peça com streaming
# ---------------------------------------------------------------------------

def estagiario_redigir(
    contrato: dict,
    codigo: str,
) -> Generator[str, None, None]:
    """Envia o contrato para o estagiário e faz streaming da peça."""
    system_base      = carregar_system_estagiario()
    contexto_minutas = contexto_completo_estagiario(codigo)
    system           = f"{system_base}\n\n{contexto_minutas}"

    prompt = f"""
Você recebeu o seguinte contrato do advogado. Redija a peça processual completa.

CONTRATO:
{json.dumps(contrato, ensure_ascii=False, indent=2)}

Ao finalizar, inclua:
1. A peça completa formatada
2. Um bloco `## CHECKLIST DE ADERÊNCIA` com itens verificados
3. Um bloco `## PENDÊNCIAS` com campos [A PREENCHER] que restarem
""".strip()

    stream = _client().chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=_montar_messages(system, [{"role": "user", "content": prompt}]),
        stream=True,
    )

    for chunk in stream:
        texto = chunk.choices[0].delta.content or ""
        yield texto


# ---------------------------------------------------------------------------
# DELTA — revisão incremental pelo advogado
# ---------------------------------------------------------------------------

def advogado_delta(
    peca_atual: str,
    instrucao_delta: str,
    contrato: dict,
) -> Generator[str, None, None]:
    """Aplica um delta pontual na peça gerada."""
    system = carregar_system_advogado()

    prompt = f"""
Aplique o delta abaixo na peça processual. Altere SOMENTE o trecho indicado.
Preserve tudo que não foi mencionado. Retorne a peça completa corrigida.

INSTRUÇÃO DO DELTA:
{instrucao_delta}

CONTRATO VIGENTE:
{json.dumps(contrato, ensure_ascii=False, indent=2)}

PEÇA ATUAL:
{peca_atual}
""".strip()

    stream = _client().chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=_montar_messages(system, [{"role": "user", "content": prompt}]),
        stream=True,
    )

    for chunk in stream:
        texto = chunk.choices[0].delta.content or ""
        yield texto
