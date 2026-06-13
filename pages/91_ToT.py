"""
91_ToT.py — Tree of Thoughts: exploracao de ramos de raciocinio.
"""
import streamlit as st
from ui.components import cabecalho
from ui.adapters import get_state_machine
from ui.layout import render_sidebar, apply_theme_css

st.set_page_config(page_title="ToT - Agente Juridico IA", layout="centered", initial_sidebar_state="collapsed")

render_sidebar()
apply_theme_css()
cabecalho()

st.subheader("Tree of Thoughts")
st.caption("Exploracao de ramos de raciocinio juridico.")

st.info("O modulo Tree of Thoughts permite explorar diferentes linhas de argumentacao para a peca processual.")

peca = get_state_machine().get("peca_gerada", "")
if peca:
    st.markdown("**Peca atual:**")
    st.markdown(peca[:500] + "...")

st.divider()
if st.button("Voltar ao fluxo principal"):
    sm = get_state_machine()
    from ui.layout import ETAPA_PAGE
    st.switch_page(ETAPA_PAGE[sm.etapa_atual])
