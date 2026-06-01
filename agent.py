"""
agent.py — Camada de chamadas via OpenRouter + RAG.
OpenRouter expõe API compatível com OpenAI; usa openai SDK apontando para
https://openrouter.ai/api/v1

Geração de peças usa RAG (rag.py) para recuperar trechos relevantes da
knowledge base em vez de enviar o conteúdo inteiro dos arquivos .md.
"""
import json
import os
from typing import Generator

os.environ["PYTHONIOENCODING"] = "utf-8"

import streamlit as st
from openai import OpenAI
from text_utils import normalize_utf8_strict, normalize_ascii_safe
from knowledge import carregar_system_advogado
import rag

from knowledge import (
    carregar_system_advogado,
    carregar_system_estagiario,
    contexto_completo_estagiario,
)

# ---------------------------------------------------------------------------
# Configuração — Free Models Router do OpenRouter
# ---------------------------------------------------------------------------
# Fonte: https://openrouter.ai/openrouter/free
# Use o router openrouter/free para selecao automatica de modelo gratuito.
# Fallbacks individuais caso o router nao esteja disponivel.
# ---------------------------------------------------------------------------
MODEL_PRIMARY   = "openrouter/free"
MODELS_FALLBACK = [
    "openai/gpt-4o-mini:free",
    "meta-llama/llama-4-maverick:free",
    "google/gemini-2.0-flash-exp:free",
]
MAX_TOKENS = 2048
MODEL = MODEL_PRIMARY


def _safe(value) -> str:
    try:
        return normalize_utf8_strict(value)
    except Exception:
        return repr(value)


def _try_chat_completion(**kwargs):
    """
    Tenta criar uma chat completion com MODEL atual.
    Em erro 404/402/429, tenta automaticamente MODELS_FALLBACK.
    Lança a última exceção se todos falharem.
    """
    client = _client()
    erros = []
    modelos = [MODEL] + MODELS_FALLBACK

    for modelo in modelos:
        try:
            return client.chat.completions.create(
                model=modelo,
                max_tokens=MAX_TOKENS,
                stream=kwargs.get("stream", False),
                messages=kwargs["messages"],
            )
        except Exception as exc:
            erros.append((modelo, exc))
            continue

    raise erros[-1][1]


@st.cache_resource(show_spinner=False)
def _client() -> OpenAI:
    api_key = st.secrets.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY não configurada em .streamlit/secrets.toml")
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            # ASCII-only obrigatorio para httpx
            "HTTP-Referer": st.secrets.get("APP_URL", "http://localhost:8501"),
            "X-Title":      normalize_ascii_safe(st.secrets.get("APP_NAME", "Agente Juridico")),
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
    Usa fallback automatico de modelo em caso de 404/402/429.
    """
    system = carregar_system_advogado()
    historico.append({"role": "user", "content": mensagem_usuario})

    stream = _try_chat_completion(
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
- Descrição: {normalize_utf8_strict(descricao_caso)}
- Domínio: {normalize_utf8_strict(dominio)} — {normalize_utf8_strict(dominio_nome)}
- Código da peça: {normalize_utf8_strict(codigo)} — {normalize_utf8_strict(codigo_nome)}
- Modo: {normalize_utf8_strict(modo)}
- Dados coletados:
{json.dumps(dados_coletados, ensure_ascii=False, indent=2)}

CAMPOS OBRIGATÓRIOS DO JSON:
{{
  "escopo": "resumo dos fatos e tipo de peça",
  "tipo_peca": "{normalize_ascii_safe(codigo)} — {normalize_ascii_safe(codigo_nome)}",
  "dominio": "{normalize_ascii_safe(dominio)} — {normalize_ascii_safe(dominio_nome)}",
  "modo": "{normalize_ascii_safe(modo)}",
  "pedidos": ["pedido 1", "pedido 2"],
  "criterios_aceite": ["critério 1", "critério 2"],
  "regras_criticas": ["regra crítica específica do código {normalize_ascii_safe(codigo)}"],
  "dados": {json.dumps(dados_coletados, ensure_ascii=False)},
  "dependencias": ["fontes.md", "verbetesSTJ.md"],
  "observacoes": "observações adicionais do advogado"
}}
""".strip()

    resposta = _try_chat_completion(
        messages=_montar_messages(system, [{"role": "user", "content": prompt}]),
        stream=False,
    )

    texto = resposta.choices[0].message.content.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()

    try:
        if isinstance(texto, bytes):
            texto = texto.decode("utf-8", errors="replace")
        if not isinstance(texto, str):
            texto = str(texto)
        try:
            parsed = json.loads(texto)
        except Exception as exc:
            st.warning(f"Falha ao interpretar briefing (JSON invalido): {exc}")
            parsed = None

        if isinstance(parsed, dict):
            return {
                "escopo": _safe(parsed.get("escopo", descricao_caso)),
                "tipo_peca": _safe(parsed.get("tipo_peca", f"{codigo} — {codigo_nome}")),
                "dominio": _safe(parsed.get("dominio", f"{dominio} — {dominio_nome}")),
                "modo": _safe(parsed.get("modo", modo)),
                "pedidos": [ _safe(x) for x in parsed.get("pedidos", []) ],
                "criterios_aceite": [ _safe(x) for x in parsed.get("criterios_aceite", []) ],
                "regras_criticas": [ _safe(x) for x in parsed.get("regras_criticas", []) ],
                "dados": dados_coletados,
                "dependencias": [ _safe(x) for x in parsed.get("dependencias", []) ],
                "observacoes": _safe(parsed.get("observacoes", texto)),
            }
    except Exception as exc:
        st.warning(f"Erro inesperado no briefing: {exc}")

    return {
        "escopo": _safe(descricao_caso),
        "tipo_peca": _safe(f"{codigo} — {codigo_nome}"),
        "dominio": _safe(f"{dominio} — {dominio_nome}"),
        "modo": _safe(modo),
        "pedidos": ["[A PREENCHER]"],
        "criterios_aceite": ["Peça aderente aos fatos", "Todos os pedidos presentes"],
        "regras_criticas": [],
        "dados": dados_coletados,
        "dependencias": [],
        "observacoes": _safe(texto),
    }


# ---------------------------------------------------------------------------
# ESTAGIÁRIO — redação da peça com streaming
# ---------------------------------------------------------------------------

def estagiario_redigir(
    contrato: dict,
    codigo: str,
) -> Generator[str, None, None]:
    """
    Usa RAG para redigir a peça:
    - Recupera trechos relevantes da knowledge base
    - Monta prompt enxuto com os trechos + contrato
    - Faz streaming da resposta
    """
    descricao = contrato.get("escopo", "")
    dominio_nome = contrato.get("dominio", "")
    codigo_nome = contrato.get("tipo_peca", "")
    modo = contrato.get("modo", "")
    dados = contrato.get("dados", {})

    prompt = rag.construir_prompt_rag(
        descricao_caso=descricao,
        dominio=contrato.get("dominio", "").split(" — ")[0],
        dominio_nome=contrato.get("dominio", ""),
        codigo=str(codigo),
        codigo_nome=str(codigo_nome),
        modo=str(modo),
        dados_coletados=dados,
    )

    stream = _try_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        texto = chunk.choices[0].delta.content or ""
        yield texto


def advogado_delta(
    peca_atual: str,
    instrucao_delta: str,
    contrato: dict,
) -> Generator[str, None, None]:
    """Aplica um delta pontual na peça gerada."""
    system = carregar_system_advogado()

    prompt = f"""
You are a Brazilian legal assistant. Reply in Brazilian Portuguese always.

Apply the delta below to the procedural document. Change ONLY the indicated section.
Preserve everything not mentioned. Return the full corrected document.

DELTA INSTRUCTION:
{normalize_utf8_strict(instrucao_delta)}

CURRENT CONTRACT:
{json.dumps(contrato, ensure_ascii=False, indent=2)}

CURRENT DOCUMENT:
{normalize_utf8_strict(peca_atual)}
""".strip()

    stream = _try_chat_completion(
        messages=_montar_messages(system, [{"role": "user", "content": prompt}]),
        stream=True,
    )

    for chunk in stream:
        texto = chunk.choices[0].delta.content or ""
        yield texto
