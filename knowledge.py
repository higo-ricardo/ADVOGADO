"""
knowledge.py — Carrega e cacheia os arquivos .md da knowledge base.
Os arquivos devem estar na pasta knowledge/ junto com o app.
"""
import streamlit as st
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"

# Mapa código de peça → arquivo de minuta
MINUTA_POR_CODIGO: dict[str, str] = {
    # Domínio A
    "RPO": "minutas-imobiliarias.md",
    "MPO": "minutas-imobiliarias.md",
    "IPR": "minutas-imobiliarias.md",
    "IPO": "minutas-imobiliarias.md",
    "REI": "minutas-imobiliarias.md",
    "CUS": "minutas-imobiliarias.md",
    "ANU": "minutas-imobiliarias.md",
    "PAF": "minutas-imobiliarias.md",
    "VIZ": "minutas-imobiliarias.md",
    "DMT": "minutas-imobiliarias.md",
    # Domínio B
    "PI":  "minutas-consumeristas.md",
    "NEG": "minutas-consumeristas.md",
    "PSC": "minutas-consumeristas.md",
    "PSN": "minutas-consumeristas.md",
    "TEL": "minutas-consumeristas.md",
    "TRO": "minutas-consumeristas.md",
    "TRB": "minutas-consumeristas.md",
    "DIS": "minutas-consumeristas.md",
    "CEL": "minutas-consumeristas.md",
    "RPR": "minutas-consumeristas.md",
    "OBF": "minutas-consumeristas.md",
    "RI":  "minutas-consumeristas.md",
    "CR":  "minutas-consumeristas.md",
    "ED":  "minutas-consumeristas.md",
    "AI":  "minutas-consumeristas.md",
    # Domínio C
    "ATR": "minutas-civeis.md",
    "ALU": "minutas-civeis.md",
    "REP": "minutas-civeis.md",
    # Domínio D
    "CHO": "documentos.md",
    "PRO": "documentos.md",
    "DHI": "documentos.md",
    "SUB": "minutas-intermediariais.md",
    "HAB": "minutas-intermediariais.md",
    "ACO": "minutas-intermediariais.md",
    "ALV": "minutas-intermediariais.md",
    "CPS": "minutas-intermediariais.md",
    # Domínio F
    "NEP": "minutas-familia.md",
    "INP": "minutas-familia.md",
    "ALI": "minutas-familia.md",
    "EXA": "minutas-familia.md",
    "INV": "minutas-familia.md",
    "OFA": "minutas-familia.md",
    "UNE": "minutas-familia.md",
    "INT": "minutas-familia.md",
    "GUA": "minutas-familia.md",
    "VIS": "minutas-familia.md",
    "CUR": "minutas-familia.md",
    "DIV": "minutas-familia.md",
    # Domínio G
    "AP":  "remedios-constitucionais.md",
    "HC":  "remedios-constitucionais.md",
    "HD":  "remedios-constitucionais.md",
    "MS":  "remedios-constitucionais.md",
    # Domínio R
    "APE": "recursos-civeis.md",
    "AGI": "recursos-civeis.md",
    "EDC": "recursos-civeis.md",
    "AGR": "recursos-civeis.md",
    "RES": "recursos-civeis.md",
    "REX": "recursos-civeis.md",
}


@st.cache_data(show_spinner=False)
def _ler_arquivo(nome: str) -> str:
    """Lê e cacheia um arquivo .md da knowledge base."""
    caminho = KNOWLEDGE_DIR / nome
    if caminho.exists():
        return caminho.read_text(encoding="utf-8")
    return f"[Arquivo {nome} não encontrado na knowledge base]"


def carregar_system_advogado() -> str:
    return _ler_arquivo("advogado.md")


def carregar_system_estagiario() -> str:
    return _ler_arquivo("estagiario.md")


def carregar_estilo() -> str:
    return _ler_arquivo("estilo_juridico.md")


def carregar_minuta_base() -> str:
    return _ler_arquivo("minuta-base.md")


def carregar_fontes() -> str:
    base = _ler_arquivo("fontes.md")
    stf  = _ler_arquivo("verbetesSTF.md")
    stj  = _ler_arquivo("verbetesSTJ.md")
    sv   = _ler_arquivo("sumulas-vinculantes.md")
    return f"{base}\n\n{stf}\n\n{stj}\n\n{sv}"


def carregar_minuta_do_codigo(codigo: str) -> str:
    nome = MINUTA_POR_CODIGO.get(codigo)
    if not nome:
        return "[Minuta não mapeada para este código]"
    return _ler_arquivo(nome)


def contexto_completo_estagiario(codigo: str) -> str:
    """Monta contexto completo que o estagiário precisa para redigir."""
    return "\n\n---\n\n".join([
        "# ESTILO DE REDAÇÃO\n" + carregar_estilo(),
        "# FRAGMENTOS DE FORMATAÇÃO\n" + carregar_minuta_base(),
        f"# MINUTAS — CÓDIGO {codigo}\n" + carregar_minuta_do_codigo(codigo),
        "# FUNDAMENTAÇÃO NORMATIVA\n" + carregar_fontes(),
    ])
