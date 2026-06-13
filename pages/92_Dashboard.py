"""
92_Dashboard.py — Dashboard de metricas e estatisticas.
"""
import streamlit as st
from ui.components import card_info
from ui.adapters import get_state_machine
from ui.layout import render_page, ETAPA_PAGE

render_page("Dashboard - Agente Juridico IA")

st.subheader("Dashboard")
st.caption("Metricas e estatisticas do sistema.")

col1, col2, col3 = st.columns(3)
with col1:
    card_info("Casos", "0", "blue")
with col2:
    card_info("Pecas geradas", "0", "green")
with col3:
    card_info("Taxa de sucesso", "-", "orange")

st.markdown("**Ultimas atividades**")
st.info("Historico de atividades sera exibido aqui.")

st.divider()
if st.button("Voltar ao fluxo principal"):
    sm = get_state_machine()
    from ui.layout import ETAPA_PAGE
    st.switch_page(ETAPA_PAGE[sm.etapa_atual])
