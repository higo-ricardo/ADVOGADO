# -*- coding: utf-8 -*-
"""
app.py — Entry point do Agente Juridico.
Redireciona para a pagina correta baseado no estado atual.
"""
import sys
import os

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

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

from core.state_machine import Etapa
from ui.adapters import get_state_machine
from ui.layout import ETAPA_PAGE

sm = get_state_machine()
etapa = sm.etapa_atual
target = ETAPA_PAGE.get(etapa, "pages/01_Triagem.py")
st.switch_page(target)