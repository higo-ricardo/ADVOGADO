"""
ui/components.py — Componentes reutilizáveis da interface.
Estética jurídica profissional com ícones visuais e importação de templates.
"""
import streamlit as st
from pathlib import Path
from core.state_machine import Etapa, ETAPA_LABEL
from ui.adapters import get_state_machine
from ui.themes import COLORS, ETAPA_ICONS, get_component_styles, format_style_dict


def template_uploader():
    """Uploader de templates personalizados (.docx ou .txt)."""
    with st.expander("Importar Template", expanded=False):
        uploaded_file = st.file_uploader(
            "Upload de template personalizado",
            type=["docx", "txt", "md"],
            help="Faça upload de um template para reutilizar em peças futuras"
        )
        
        if uploaded_file:
            templates_dir = Path("data/templates")
            templates_dir.mkdir(parents=True, exist_ok=True)
            
            template_path = templates_dir / uploaded_file.name
            with open(template_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"Template salvo: {uploaded_file.name}")
            st.session_state.templates_disponiveis = None
        
        templates_dir = Path("data/templates")
        if templates_dir.exists():
            templates = list(templates_dir.glob("*.docx")) + list(templates_dir.glob("*.txt")) + list(templates_dir.glob("*.md"))
            if templates:
                st.caption("Templates disponíveis:")
                for t in templates:
                    st.markdown(f"- {t.name}")


def estilo_uploader():
    """Uploader de estilo jurídico personalizado."""
    with st.expander("Importar Estilo Jurídico", expanded=False):
        uploaded_file = st.file_uploader(
            "Upload de estilo personalizado",
            type=["txt", "md"],
            key="estilo_upload",
            help="Faça upload de um arquivo de estilo jurídico"
        )
        
        if uploaded_file:
            estilos_dir = Path("data/estilos")
            estilos_dir.mkdir(parents=True, exist_ok=True)
            
            estilo_path = estilos_dir / uploaded_file.name
            with open(estilo_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"Estilo salvo: {uploaded_file.name}")


def barra_progresso():
    """Exibe barra de progresso com as 6 etapas."""
    sm = get_state_machine()
    etapas = list(Etapa)
    idx = etapas.index(sm.etapa_atual)
    total = len(etapas)
    
    cols = st.columns(total)
    
    for i, (col, etapa) in enumerate(zip(cols, etapas)):
        with col:
            active = i == idx
            if active:
                styles = get_component_styles("progress_step_active")
                label_color = COLORS["primary"]
            else:
                styles = get_component_styles("progress_step_inactive")
                label_color = "#64748b"
            
            st.markdown(
                f"""
                <div style="{format_style_dict(styles)}">{ETAPA_ICONS[i]}</div>
                <div style="text-align:center; font-size:10px; margin-top:4px; color:{label_color};">
                    {ETAPA_LABEL[etapa][:12]}
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.progress((idx) / (total - 1))


def cabecalho():
    """Cabeçalho fixo do app - estilo jurídico."""
    col1, col2, col3 = st.columns([5, 1, 1])
    
    with col1:
        st.markdown(
            """
            <div style="margin-bottom:8px;">
                <span style="font-size:28px; font-weight:700; color:#1e3a8a;">Agente Jurídico IA</span>
                <div style="font-size:14px; color:#64748b;">Sistema especializado em peças processuais</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div style="text-align:center; padding:8px;">
                <span style="color:#10b981; font-size:12px;">● Online</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        if st.button("Reiniciar", help="Começa um novo caso", use_container_width=True):
            sm = get_state_machine()
            sm.reiniciar()
            st.rerun()
    
    st.divider()


def card_info(titulo: str, conteudo: str, cor: str = "blue"):
    """Card de informação com estilo jurídico."""
    cores = {
        "blue": COLORS["primary"],
        "green": COLORS["success"],
        "orange": COLORS["warning"],
        "red": COLORS["error"],
    }
    hex_cor = cores.get(cor, COLORS["primary"])
    is_dark = st.session_state.get("dark_mode", False)
    
    if is_dark:
        styles = get_component_styles("card_dark")
        text_color = COLORS["text_dark"]
    else:
        styles = get_component_styles("card")
        text_color = COLORS["text_light"]
    
    # Atualiza cor da borda
    styles["border_left"] = f"4px solid {hex_cor}"
    
    st.markdown(
        f"""
        <div style="{format_style_dict(styles)}">
            <strong style="color:{hex_cor}; font-size:14px;">{titulo}</strong>
            <div style="color:{text_color}; margin-top:6px; font-size:13px;">{conteudo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_codigo(codigo: str, nome: str):
    """Badge visual para o código da peça."""
    styles = get_component_styles("badge")
    st.markdown(
        f"""
        <div style="{format_style_dict(styles)}">{codigo} - {nome}</div>
        """,
        unsafe_allow_html=True
    )


def alerta_erro(msg: str):
    """Alerta de erro estilizado."""
    styles = get_component_styles("alert_error")
    st.markdown(
        f"""
        <div style="{format_style_dict(styles)}">
            <span style="color:{COLORS['error']}; font-weight:500;">⚠ {msg}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def checklist_visual(itens: list[str]):
    """Exibe checklist com estilo jurídico."""
    styles_item = get_component_styles("checklist_item")
    for item in itens:
        if item.strip():
            st.markdown(
                f"""
                <div style="{format_style_dict(styles_item)}">
                    <span style="color:{COLORS['success']}; font-weight:bold;">✓</span>
                    <span style="margin-left:8px;">{item}</span>
                </div>
                """,
                unsafe_allow_html=True
            )