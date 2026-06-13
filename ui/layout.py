"""
ui/layout.py — Layout compartilhado entre páginas standalone.
"""
import streamlit as st
from core.state_machine import Etapa
from ui.components import template_uploader, estilo_uploader


ETAPA_PAGE: dict[Etapa, str] = {
    Etapa.TRIAGEM:     "pages/01_Triagem.py",
    Etapa.CONFIRMACAO: "pages/02_Confirmacao.py",
    Etapa.COLETA:      "pages/03_Coleta.py",
    Etapa.CONTRATO:    "pages/04_Briefing.py",
    Etapa.GERACAO:     "pages/05_Geracao.py",
    Etapa.REVISAO:     "pages/06_Revisao.py",
}


def render_sidebar():
    with st.sidebar:
        st.markdown("### Configuracoes")

        dark_mode = st.toggle(
            "Tema escuro",
            value=st.session_state.get("dark_mode", False),
            help="Ativa modo noturno",
        )

        if dark_mode != st.session_state.get("dark_mode", False):
            st.session_state.dark_mode = dark_mode
            st.rerun()

        st.markdown("---")
        template_uploader()
        estilo_uploader()

        st.markdown("---")
        st.caption("Agente Juridico IA v1.0.0")


def apply_theme_css():
    if st.session_state.get("dark_mode", False):
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
