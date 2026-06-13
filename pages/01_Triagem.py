"""
01_Triagem.py — Etapa 1: Usuario descreve o caso.
"""
import streamlit as st
from core.state_machine import Etapa
from core.router import detectar_dominio
from ui.components import alerta_erro
from ui.adapters import get_state_machine
from ui.layout import render_page, ETAPA_PAGE
from utils.input_validation import validate_description

render_page("Triagem - Agente Juridico IA")

st.subheader("Descreva o caso")
st.caption("Escreva livremente. O sistema identificara o tipo de peca adequada.")

with st.form("form_triagem"):
    descricao = st.text_area(
        "O que aconteceu?",
        height=160,
        placeholder=(
            "Ex: Meu cliente foi esbulhado de sua propriedade rural ha 3 meses. "
            "O invasor entrou de madrugada e nao quer sair..."
        ),
        value=get_state_machine().get("descricao_caso", ""),
    )
    enviado = st.form_submit_button("Analisar caso →", type="primary", use_container_width=True)

if enviado:
    validacao = validate_description(descricao)
    if not validacao.is_valid:
        if validacao.severity.value == "critical":
            alerta_erro(f"⛔ {validacao.message}")
        else:
            alerta_erro(validacao.message)
        st.stop()

    descricao_limpa = validacao.sanitized_value or descricao
    get_state_machine().set("descricao_caso", descricao_limpa)

    resultado = detectar_dominio(descricao_limpa)
    if resultado:
        dom_id, dom_nome = resultado
        get_state_machine().set("dominio", dom_id)
        get_state_machine().set("dominio_nome", dom_nome)

    get_state_machine().avancar(Etapa.CONFIRMACAO)
    st.rerun()
