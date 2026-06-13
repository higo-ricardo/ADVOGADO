"""
05_Geracao.py — Etapa 5: Geracao da peca (streaming).
"""
import streamlit as st
from core.state_machine import Etapa
from ui.components import badge_codigo, alerta_erro
from ui.adapters import get_state_machine, get_adapter
from ui.layout import render_page

render_page("Geracao - Agente Juridico IA")

st.subheader("Gerando a peca processual")

codigo   = get_state_machine().get("codigo_peca")
cod_nome = get_state_machine().get("codigo_nome")
contrato = get_state_machine().get("contrato")

badge_codigo(codigo, cod_nome)
st.caption("A peca esta sendo redigida. Aguarde...")

peca_existente = get_state_machine().get("peca_gerada", "")

if not peca_existente:
    container = st.empty()

    try:
        with st.spinner("Estagiario redigindo..."):
            stream = get_adapter().estagiario_redigir(contrato, codigo)
            buffer = ""
            for chunk in stream:
                buffer += chunk
                container.markdown(buffer)
            peca_completa = buffer
    except Exception as e:
        alerta_erro(f"Erro na geracao: {e}")
        if st.button("Tentar novamente"):
            st.rerun()
        st.stop()

    get_state_machine().set("peca_gerada", peca_completa)
    get_state_machine().avancar(Etapa.REVISAO)
    st.rerun()
else:
    get_state_machine().avancar(Etapa.REVISAO)
    st.rerun()
