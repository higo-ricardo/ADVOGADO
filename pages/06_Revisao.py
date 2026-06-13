"""
06_Revisao.py — Etapa 6: Revisao, checklist, delta e download.
"""
import streamlit as st
from core.state_machine import Etapa
from ui.components import cabecalho, barra_progresso, badge_codigo, checklist_visual, alerta_erro
from ui.adapters import get_state_machine, get_adapter
from ui.layout import render_sidebar, apply_theme_css
from utils import export

st.set_page_config(page_title="Revisao - Agente Juridico IA", layout="centered", initial_sidebar_state="collapsed")

render_sidebar()
apply_theme_css()
cabecalho()
barra_progresso()
st.markdown("")

st.subheader("Revisao e download")

codigo   = get_state_machine().get("codigo_peca")
cod_nome = get_state_machine().get("codigo_nome")
contrato = get_state_machine().get("contrato", {})
peca     = get_state_machine().get("peca_gerada", "")
dados    = get_state_machine().get("dados_coletados", {})

badge_codigo(codigo, cod_nome)

tab_peca, tab_check, tab_delta = st.tabs(["Peca", "Checklist", "Solicitar ajuste"])

with tab_peca:
    corpo = peca.split("## CHECKLIST")[0].strip()
    st.markdown(corpo)

with tab_check:
    criterios = contrato.get("criterios_aceite", [])
    if criterios:
        st.markdown("**Criterios de aceite verificados:**")
        checklist_visual(criterios)
    else:
        st.info("Nenhum criterio de aceite registrado no contrato.")

    pendencias = [l.strip() for l in peca.split("\n") if "[A PREENCHER]" in l]
    if pendencias:
        st.warning(f"{len(pendencias)} campo(s) precisam ser preenchidos manualmente:")
        for p in pendencias:
            st.markdown(f"- `{p}`")

with tab_delta:
    st.caption("Solicite uma alteracao pontual sem reescrever a peca inteira.")
    instrucao = st.text_area(
        "O que deve ser alterado?",
        placeholder="Ex: No 3o paragrafo, adicione referencia ao art. 927 do CC. / Corrija o nome do reu para Joao da Silva.",
        height=100,
    )
    if st.button("Aplicar ajuste", type="primary"):
        if instrucao.strip():
            with st.spinner("Aplicando delta..."):
                stream = get_adapter().advogado_delta(peca, instrucao, contrato)
                nova_peca = st.write_stream(stream)
            get_state_machine().set("peca_gerada", str(nova_peca) if not isinstance(nova_peca, str) else nova_peca)
            st.success("Ajuste aplicado!")
            st.rerun()
        else:
            st.warning("Descreva o ajuste desejado.")

st.divider()

st.markdown("**Baixar peca**")
col1, col2 = st.columns(2)

with col1:
    autor = dados.get("autor", dados.get("requerente", dados.get("exequente", "parte")))
    nome_txt = export.nome_arquivo_peca(codigo, autor).replace(".docx", ".txt")
    st.download_button(
        label="Baixar como .txt",
        data=peca.encode("utf-8"),
        file_name=nome_txt,
        mime="text/plain",
        use_container_width=True,
    )

with col2:
    if export.DOCX_DISPONIVEL:
        try:
            docx_bytes = export.gerar_docx(peca, codigo)
            nome_docx = export.nome_arquivo_peca(codigo, autor)
            st.download_button(
                label="Baixar como .docx",
                data=docx_bytes,
                file_name=nome_docx,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.warning(f"Erro ao gerar .docx: {e}")
    else:
        st.info("Para download em .docx, instale: pip install python-docx")

st.divider()
if st.button("Novo caso", use_container_width=True):
    get_state_machine().reiniciar()
    st.rerun()
