"""
03_Coleta.py — Etapa 3: Coleta de dados obrigatorios.
"""
import streamlit as st
from core.state_machine import Etapa
from core.router import campos_do_codigo
from ui.components import cabecalho, barra_progresso, badge_codigo, alerta_erro
from ui.adapters import get_state_machine
from ui.layout import render_sidebar, apply_theme_css
from utils.input_validation import validate_campo_personalizado

st.set_page_config(page_title="Coleta - Agente Juridico IA", layout="centered", initial_sidebar_state="collapsed")

render_sidebar()
apply_theme_css()
cabecalho()
barra_progresso()
st.markdown("")

codigo    = get_state_machine().get("codigo_peca")
cod_nome  = get_state_machine().get("codigo_nome")
dom_nome  = get_state_machine().get("dominio_nome")

st.subheader("Dados do caso")
badge_codigo(codigo, cod_nome)
st.caption(f"Dominio: {dom_nome}")

campos = campos_do_codigo(codigo)
dados_anteriores = get_state_machine().get("dados_coletados", {})

with st.form("form_coleta"):
    valores = {}

    for campo in campos:
        cid    = campo["id"]
        label  = campo["label"] + " *"
        tipo   = campo.get("tipo", "text")
        val    = dados_anteriores.get(cid, "")

        if tipo == "textarea":
            valores[cid] = st.text_area(label, value=val, height=100, key=f"campo_{cid}")
        elif tipo == "select":
            opcoes = campo.get("opcoes", [])
            idx = opcoes.index(val) if val in opcoes else 0
            valores[cid] = st.selectbox(label, options=opcoes, index=idx, key=f"campo_{cid}")
        else:
            valores[cid] = st.text_input(label, value=val, key=f"campo_{cid}")

    col1, col2 = st.columns(2)
    with col1:
        voltar = st.form_submit_button("<- Voltar")
    with col2:
        avancar = st.form_submit_button("Gerar briefing ->", type="primary", use_container_width=True)

if voltar:
    get_state_machine().avancar(Etapa.CONFIRMACAO)
    st.rerun()

if avancar:
    erros_validacao = []
    valores_sanitizados = {}

    for campo in campos:
        cid = campo["id"]
        label = campo["label"]
        valor = valores.get(cid, "")

        if campo.get("tipo") == "select":
            valores_sanitizados[cid] = valor
            continue

        if not valor.strip():
            erros_validacao.append(label)
            continue

        validacao = validate_campo_personalizado(
            valor=valor,
            label=label,
            obrigatorio=True,
            min_chars=1,
            max_chars=500,
            tipo="legal",
        )

        if not validacao.is_valid:
            if validacao.severity.value in ("critical", "error"):
                alerta_erro(f"{label}: {validacao.message}")
                st.stop()

        valores_sanitizados[cid] = validacao.sanitized_value or valor

    if erros_validacao:
        alerta_erro(f"Preencha os campos: {', '.join(erros_validacao)}")
        st.stop()

    get_state_machine().set("dados_coletados", valores_sanitizados)
    get_state_machine().avancar(Etapa.CONTRATO)
    st.rerun()
