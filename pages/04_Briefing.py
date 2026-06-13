"""
04_Briefing.py — Etapa 4: Revisar briefing/contrato.
"""
import streamlit as st
from core.state_machine import Etapa
from ui.components import badge_codigo, alerta_erro
from ui.adapters import get_state_machine, get_adapter
from ui.layout import render_page

render_page("Briefing - Agente Juridico IA")

st.subheader("Briefing do caso")
st.caption("O sistema preparou o briefing abaixo. Revise antes de gerar a peca.")

codigo    = get_state_machine().get("codigo_peca")
cod_nome  = get_state_machine().get("codigo_nome")
dom_id    = get_state_machine().get("dominio")
dom_nome  = get_state_machine().get("dominio_nome")
dados     = get_state_machine().get("dados_coletados", {})
modo      = get_state_machine().get("modo")
contrato_existente = get_state_machine().get("contrato", {})

if not contrato_existente:
    with st.spinner("Preparando briefing..."):
        try:
            contrato = get_adapter().gerar_contrato(
                descricao_caso=get_state_machine().get("descricao_caso"),
                dominio=dom_id,
                dominio_nome=dom_nome,
                codigo=codigo,
                codigo_nome=cod_nome,
                dados_coletados=dados,
                modo=modo,
            )
            get_state_machine().set("contrato", contrato)
        except Exception as e:
            alerta_erro(f"Erro ao gerar briefing: {e}")
            st.stop()
    st.rerun()

contrato = get_state_machine().get("contrato")

badge_codigo(codigo, cod_nome)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Escopo**")
    st.info(contrato.get("escopo", "-"))
with col2:
    st.markdown("**Modo de operacao**")
    modo_label = "Autonomo (direto)" if modo == "autonomo" else "Integrado (advogado + estagiario)"
    st.info(modo_label)

st.markdown("**Pedidos identificados**")
for pedido in contrato.get("pedidos", []):
    st.markdown(f"- {pedido}")

st.markdown("**Criterios de aceite**")
for criterio in contrato.get("criterios_aceite", []):
    st.markdown(f"- {criterio}")

if contrato.get("regras_criticas"):
    st.markdown("**Regras criticas para este tipo de peca**")
    for regra in contrato.get("regras_criticas", []):
        st.warning(regra)

st.divider()

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("<- Voltar"):
        get_state_machine().set("contrato", {})
        get_state_machine().avancar(Etapa.COLETA)
        st.rerun()
with col2:
    if st.button("Refazer briefing"):
        get_state_machine().set("contrato", {})
        st.rerun()
with col3:
    if st.button("Gerar peca agora ->", type="primary", use_container_width=True):
        get_state_machine().avancar(Etapa.GERACAO)
        st.rerun()
