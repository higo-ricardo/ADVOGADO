"""
02_Confirmacao.py — Etapa 2: Confirmar dominio e codigo da peca.
"""
import streamlit as st
from core.state_machine import Etapa
from core.router import codigos_do_dominio, is_autonomo
from ui.components import card_info
from ui.adapters import get_state_machine
from ui.layout import render_page

render_page("Confirmacao - Agente Juridico IA")

st.subheader("Confirme o tipo de peca")

descricao = get_state_machine().get("descricao_caso")
dom_id    = get_state_machine().get("dominio")
dom_nome  = get_state_machine().get("dominio_nome")

with st.expander("Caso descrito", expanded=False):
    st.write(descricao)

dominios_opcoes = {
    "A - Imobiliario":                 "A",
    "B - Consumerista / JEC":          "B",
    "C - Civel":                       "C",
    "D - Documentos e Apoio":          "D",
    "F - Familia e Sucessoes":         "F",
    "G - Remedios Constitucionais":    "G",
    "R - Recursos Civeis":             "R",
}

idx_default = 0
if dom_id:
    for i, (label, did) in enumerate(dominios_opcoes.items()):
        if did == dom_id:
            idx_default = i
            break
    card_info("Dominio detectado automaticamente", f"{dom_id} - {dom_nome}", "green")

with st.form("form_confirmacao"):
    dominio_sel = st.selectbox(
        "Dominio juridico",
        options=list(dominios_opcoes.keys()),
        index=idx_default,
    )
    dom_id_sel = dominios_opcoes[dominio_sel]

    codigos = codigos_do_dominio(dom_id_sel)
    codigos_labels = [f"{cod} - {nome}" for cod, nome in codigos]

    codigo_sel_label = st.selectbox("Tipo de peca", options=codigos_labels)

    confirmado = st.form_submit_button("Confirmar e prosseguir →", type="primary", use_container_width=True)
    voltar     = st.form_submit_button("← Voltar")

if voltar:
    get_state_machine().avancar(Etapa.TRIAGEM)
    st.rerun()

if confirmado:
    cod, nome_cod = codigos[codigos_labels.index(codigo_sel_label)]
    dom_label = dominio_sel.split(" - ", 1)

    get_state_machine().set("dominio",      dom_id_sel)
    get_state_machine().set("dominio_nome", dom_label[1] if len(dom_label) > 1 else dominio_sel)
    get_state_machine().set("codigo_peca",  cod)
    get_state_machine().set("codigo_nome",  nome_cod)
    get_state_machine().set("modo", "autonomo" if is_autonomo(cod) else "integrado")

    get_state_machine().avancar(Etapa.COLETA)
    st.rerun()
