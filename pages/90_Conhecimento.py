"""
90_Conhecimento.py — Base de conhecimento e verbetes.
"""
import streamlit as st
from ui.adapters import get_state_machine
from ui.layout import render_page, ETAPA_PAGE

render_page("Conhecimento - Agente Juridico IA")

st.subheader("Base de Conhecimento Juridico")
st.caption("Verbetes de jurisprudencia e materiais de apoio.")

tab_verbetes, tab_materiais = st.tabs(["Verbetes", "Materiais"])

with tab_verbetes:
    st.markdown("**Pesquisar verbetes**")
    busca = st.text_input("Termo de busca", placeholder="Ex: esbulho, negativacao, alimentos...")

    if st.button("Buscar", type="primary"):
        st.info("Funcionalidade de busca sera implementada com o repositorio de verbetes.")

with tab_materiais:
    st.markdown("**Materiais de apoio**")
    st.info("Materiais juridicos de referencia disponiveis no modulo de conhecimento.")

st.divider()
if st.button("Voltar ao fluxo principal"):
    sm = get_state_machine()
    from ui.layout import ETAPA_PAGE
    st.switch_page(ETAPA_PAGE[sm.etapa_atual])
