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

import streamlit as st

st.set_page_config(
    page_title="Agente Juridico IA",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Inicializa tema no session_state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Importa text_normalization PRIMEIRO
from utils.text_normalization import normalize_ascii_safe, normalize_utf8_strict

# Importa modulos do app
from core.state_machine import AgentState, Etapa, StateMachine
from ui.components import cabecalho, barra_progresso, template_uploader, estilo_uploader
from ui.pages import (
    render_triagem,
    render_confirmacao,
    render_coleta,
    render_contrato,
    render_geracao,
    render_revisao,
)
from ui.adapters import get_state_machine, save_state_machine

# CSS base
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemOverflow, sans-serif !important; }

.stButton>button, .stDownloadButton>button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.stButton>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15) !important;
}
.stForm { border: none !important; }

/* Skeleton loading */
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
    height: 16px;
    margin: 8px 0;
}
@keyframes shimmer {
    0% { background-position: 200%; }
    100% { background-position: -200%; }
}
</style>
""", unsafe_allow_html=True)

# Sidebar com configurações
with st.sidebar:
    st.markdown("### Configurações")
    
    # Toggle de tema
    dark_mode = st.toggle(
        "Tema escuro", 
        value=st.session_state.dark_mode,
        help="Ativa modo noturno"
    )
    
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    st.markdown("---")
    template_uploader()
    estilo_uploader()
    
    st.markdown("---")
    st.caption("Agente Juridico IA v1.0.0")

# CSS dinâmico baseado no tema
if st.session_state.dark_mode:
    st.markdown("""
    <style>
    .stApp { background: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background: #1e293b; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: #1e293b; color: #f8fafc; border: 1px solid #334155;
    }
    .stSelectbox>div>div>select { background: #1e293b; color: #f8fafc; }
    [data-testid="stForm"] { background: #1e293b; }
    .stMarkdown, .stCaption { color: #cbd5e1 !important; }
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