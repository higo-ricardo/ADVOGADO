"""
app.py — Entry point do Agente Jurídico.
Executa: streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Agente Jurídico",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

import state
from state import Etapa
from ui.components import cabecalho, barra_progresso
from ui.pages import (
    render_triagem,
    render_confirmacao,
    render_coleta,
    render_contrato,
    render_geracao,
    render_revisao,
)

# CSS minimalista
st.markdown("""
<style>
.stForm { border: none !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0.5rem; }
.stButton > button { border-radius: 8px; }
.stDownloadButton > button { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Inicializa state
state.init()

# Cabeçalho e progresso
cabecalho()
barra_progresso()
st.markdown("")

# Roteamento por etapa
etapa = state.etapa_atual()

if   etapa == Etapa.TRIAGEM:      render_triagem()
elif etapa == Etapa.CONFIRMACAO:  render_confirmacao()
elif etapa == Etapa.COLETA:       render_coleta()
elif etapa == Etapa.CONTRATO:     render_contrato()
elif etapa == Etapa.GERACAO:      render_geracao()
elif etapa == Etapa.REVISAO:      render_revisao()
