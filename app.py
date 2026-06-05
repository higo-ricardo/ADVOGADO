# -*- coding: utf-8 -*-
"""
app.py — Entry point do Agente Juridico.
Executa: streamlit run app.py
"""
import sys
import os

# Ativa UTF-8 antes de qualquer import
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Força encoding UTF-8 no interpretador (Python < 3.15 compat)
try:
    sys.setdefaultencoding = lambda x: None
except AttributeError:
    pass

# Importa text_normalization PRIMEIRO para interceptar todo texto
from utils.text_normalization import normalize_ascii_safe, normalize_utf8_strict

import streamlit as st

st.set_page_config(
    page_title="Agente Juridico",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Importa modulos do app
from core.state_machine import AgentState, Etapa, StateMachine
from ui.components import cabecalho, barra_progresso
from ui.pages import (
    render_triagem,
    render_confirmacao,
    render_coleta,
    render_contrato,
    render_geracao,
    render_revisao,
)
from ui.adapters import get_state_machine, save_state_machine

# CSS minimalista — sem acentos
st.markdown("""
<style>
.stForm { border: none !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0.5rem; }
.stButton > button { border-radius: 8px; }
.stDownloadButton > button { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Inicializa state machine
state_machine = get_state_machine()

# Cabecalho e progresso
cabecalho()
barra_progresso()
st.markdown("")

# Roteamento por etapa
etapa = state_machine.etapa_atual

if   etapa == Etapa.TRIAGEM:      render_triagem()
elif etapa == Etapa.CONFIRMACAO:  render_confirmacao()
elif etapa == Etapa.COLETA:       render_coleta()
elif etapa == Etapa.CONTRATO:     render_contrato()
elif etapa == Etapa.GERACAO:      render_geracao()
elif etapa == Etapa.REVISAO:      render_revisao()
