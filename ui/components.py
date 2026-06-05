"""
ui/components.py — Componentes reutilizáveis da interface.
"""
import streamlit as st
from core.state_machine import Etapa, ETAPA_LABEL
from ui.adapters import get_state_machine


def etapa_idx() -> int:
    """Obtém o índice da etapa atual."""
    sm = get_state_machine()
    return sm.etapa_atual.value  # type: ignore


def barra_progresso():
    """Exibe barra de progresso com as 6 etapas."""
    sm = get_state_machine()
    etapas = list(Etapa)
    idx = etapas.index(sm.etapa_atual)
    total = len(etapas)

    st.progress((idx) / (total - 1), text=f"Etapa {idx + 1} de {total}: **{ETAPA_LABEL[sm.etapa_atual]}**")


def cabecalho():
    """Cabeçalho fixo do app."""
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### Agente Juridico")
    with col2:
        if st.button("Reiniciar", help="Começa um novo caso do zero"):
            sm = get_state_machine()
            sm.reiniciar()
            st.rerun()
    st.divider()


def card_info(titulo: str, conteudo: str, cor: str = "blue"):
    """Card de informação com borda colorida."""
    cores = {
        "blue":   "#1E88E5",
        "green":  "#43A047",
        "orange": "#FB8C00",
        "red":    "#E53935",
    }
    hex_cor = cores.get(cor, cores["blue"])
    st.markdown(
        f"""
        <div style="
            border-left: 4px solid {hex_cor};
            padding: 12px 16px;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
            margin-bottom: 12px;
        ">
            <strong style="color:{hex_cor}">{titulo}</strong><br>
            <span style="color:#333">{conteudo}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_codigo(codigo: str, nome: str):
    """Badge visual para o código da peça."""
    st.markdown(
        f"""
        <div style="
            display:inline-block;
            background:#1E88E5;
            color:white;
            padding:4px 12px;
            border-radius:20px;
            font-weight:bold;
            font-size:14px;
            margin-bottom:8px;
        ">{codigo} — {nome}</div>
        """,
        unsafe_allow_html=True,
    )


def alerta_erro(msg: str):
    st.error(f"Erro: {msg}")


def checklist_visual(itens: list[str]):
    """Exibe checklist com ícones visuais."""
    for item in itens:
        if item.strip():
            st.markdown(f"✅ {item}")
