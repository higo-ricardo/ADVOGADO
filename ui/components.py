"""
ui/components.py — Componentes reutilizáveis da interface.
Estética jurídica profissional com ícones visuais e importação de templates.
"""
import streamlit as st
from pathlib import Path
from core.state_machine import Etapa, ETAPA_LABEL
from ui.adapters import get_state_machine

# Paleta de cores jurídica
COLORS = {
    "primary": "#1e3a8a",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
}


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
    icons = ["📁", "✓", "📝", "📋", "✍", "🔍"]
    
    for i, (col, etapa) in enumerate(zip(cols, etapas)):
        with col:
            active = i == idx
            bg = COLORS["primary"] if active else "#e2e8f0"
            color = "white" if active else COLORS["primary"]
            st.markdown(
                f"""
                <div style="
                    display:flex; align-items:center; justify-content:center;
                    background:{bg}; color:{color}; width:32px; height:32px;
                    border-radius:50%; font-weight:bold; margin:auto; font-size:14px;
                ">{icons[i]}</div>
                <div style="text-align:center; font-size:10px; margin-top:4px; color:{'#64748b' if not active else COLORS['primary']};">
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
    cores = {"blue": COLORS["primary"], "green": COLORS["success"], "orange": COLORS["warning"], "red": COLORS["error"]}
    hex_cor = cores.get(cor, COLORS["primary"])
    is_dark = st.session_state.get("dark_mode", False)
    bg = "#1e293b" if is_dark else "#ffffff"
    text = "#f8fafc" if is_dark else "#1e293b"
    
    st.markdown(
        f"""
        <div style="
            border-left: 4px solid {hex_cor};
            padding: 16px 20px;
            background: {bg};
            border-radius: 8px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        ">
            <strong style="color:{hex_cor}; font-size:14px;">{titulo}</strong>
            <div style="color:{text}; margin-top:6px; font-size:13px;">{conteudo}</div>
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
            background:{COLORS['primary']};
            color:white;
            padding:6px 14px;
            border-radius:20px;
            font-weight:600;
            font-size:13px;
            margin-bottom:12px;
        ">{codigo} - {nome}</div>
        """,
        unsafe_allow_html=True
    )


def alerta_erro(msg: str):
    """Alerta de erro estilizado."""
    st.markdown(
        f"""
        <div style="
            background:#fef2f2; border-left:4px solid {COLORS['error']};
            padding:12px 16px; border-radius:8px; margin:12px 0;
        "><span style="color:{COLORS['error']}; font-weight:500;">⚠ {msg}</span></div>
        """,
        unsafe_allow_html=True
    )


def checklist_visual(itens: list[str]):
    """Exibe checklist com estilo jurídico."""
    for item in itens:
        if item.strip():
            st.markdown(
                f"""
                <div style="margin:6px 0; padding:4px 0;">
                    <span style="color:{COLORS['success']}; font-weight:bold;">✓</span>
                    <span style="margin-left:8px;">{item}</span>
                </div>
                """,
                unsafe_allow_html=True
            )