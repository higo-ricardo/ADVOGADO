"""
rag.py — Retrieval-Augmented Generation para a knowledge base.
Indexa os arquivos .md de knowledge/ com embeddings locais (all-MiniLM-L6-v2)
e recupera trechos relevantes para compor prompts menores e mais precisos.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
from text_utils import normalize_utf8_strict

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
MODEL_NAME = "all-MiniLM-L6-v2"
KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
INDEX_DIR = Path(__file__).parent / "knowledge_index"
INDEX_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Estado compartilhado
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _get_model() -> SentenceTransformer:
    """Carrega o modelo de embeddings (cacheado para não recarregar)."""
    return SentenceTransformer(MODEL_NAME)


@st.cache_resource(show_spinner=False)
def _get_index() -> dict:
    """Carrega ou cria o índice FAISS."""
    return {"vectors": None, "ids": [], "textos": []}


# ---------------------------------------------------------------------------
# Indexação
# ---------------------------------------------------------------------------
def _chunk_text(text: str, size: int = 400, overlap: int = 80) -> list[str]:
    """Divide texto em chunks com sobreposição para preservar contexto."""
    if not text.strip():
        return []
    words = text.split()
    chunks: list[str] = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + size])
        chunks.append(chunk)
        i += size - overlap
    return chunks


def _indexar_base() -> None:
    """Indexa todos os arquivos .md da pasta knowledge/."""
    modelo = _get_model()
    idx = _get_index()
    if idx["vectors"] is not None:
        return

    textos: list[str] = []
    ids: list[str] = []

    for arquivo in sorted(KNOWLEDGE_DIR.rglob("*.md")):
        texto = arquivo.read_text(encoding="utf-8", errors="replace")
        texto = normalize_utf8_strict(texto)
        chunks = _chunk_text(texto)
        for i, chunk in enumerate(chunks):
            textos.append(chunk)
            ids.append(f"{arquivo.stem}::{i}")

    if not textos:
        idx["vectors"] = np.zeros((0, 384), dtype=np.float32)
        return

    embeddings = modelo.encode(textos, normalize_embeddings=True)
    idx["vectors"] = np.array(embeddings, dtype=np.float32)
    idx["ids"] = ids
    idx["textos"] = textos


def rebuild_index() -> None:
    """Força reconstrução do índice (útil após alterar arquivos .md)."""
    idx = _get_index()
    idx["vectors"] = None
    idx["ids"] = []
    idx["textos"] = []
    _indexar_base()


# ---------------------------------------------------------------------------
# Busca
# ---------------------------------------------------------------------------
def buscar(consulta: str, top_k: int = 3) -> list[dict[str, Any]]:
    """
    Busca os trechos mais relevantes da knowledge base.
    Retorna lista de dicts: {id, texto, score}
    """
    _indexar_base()
    idx = _get_index()

    if idx["vectors"] is None or len(idx["textos"]) == 0:
        return []

    modelo = _get_model()
    query_vec = modelo.encode([consulta], normalize_embeddings=True)
    scores = (idx["vectors"] @ query_vec[0]).astype(np.float32)

    k = min(top_k, len(scores))
    top_indices = np.argpartition(-scores, k - 1)[:k]
    top_indices = top_indices[np.argsort(-scores[top_indices])]

    resultados = []
    for rank, i in enumerate(top_indices):
        resultados.append(
            {
                "id": idx["ids"][i],
                "texto": idx["textos"][i],
                "score": float(scores[i]),
            }
        )
    return resultados


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------
def construir_prompt_rag(
    descricao_caso: str,
    dominio: str,
    dominio_nome: str,
    codigo: str,
    codigo_nome: str,
    modo: str,
    dados_coletados: dict,
) -> str:
    """
    Monta o prompt para o LLM usando RAG:
    - Recupera trechos relevantes da base
    - Inclui apenas o necessário no prompt
    """
    consulta = f"{codigo} {codigo_nome} {dominio} {descricao_caso[:200]}"
    trechos = buscar(consulta, top_k=4)

    contexto_rag = "\n\n".join(
        f"[Trecho {i+1}]\n{t['texto']}" for i, t in enumerate(trechos)
    )

    prompt = f"""You are a Brazilian legal assistant. Reply in Brazilian Portuguese.

Use the reference trechos below to draft the procedural document. If a trecho is incomplete or has [A PREENCHER], keep it.

CONTEXTUAL REFERENCE (most relevant trechos from the knowledge base):
{contexto_rag}

CASE DATA:
- Description: {normalize_utf8_strict(descricao_caso)}
- Domain: {normalize_utf8_strict(dominio)} - {normalize_utf8_strict(dominio_nome)}
- Document code: {normalize_utf8_strict(codigo)} - {normalize_utf8_strict(codigo_nome)}
- Mode: {normalize_utf8_strict(modo)}
- Collected data: {json.dumps(dados_coletados, ensure_ascii=False, indent=2)}

Return a complete procedural document following the reference structure.
Include:
1. The complete formatted document
2. A "## CHECKLIST DE ADERENCIA" block with verified items
3. A "## PENDENCIAS" block with any remaining [A PREENCHER] fields.
""".strip()

    return prompt


# ---------------------------------------------------------------------------
# Cache de embeddings para reuso
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _cache_key(consulta: str, top_k: int) -> str:
    return f"{consulta[:100]}::{top_k}"


def buscar_cached(consulta: str, top_k: int = 3) -> list[dict[str, Any]]:
    """Busca com cache simples baseado na consulta."""
    key = _cache_key(consulta, top_k)
    cache = st.session_state.setdefault("rag_cache", {})
    if key in cache:
        return cache[key]
    resultados = buscar(consulta, top_k=top_k)
    cache[key] = resultados
    return resultados
