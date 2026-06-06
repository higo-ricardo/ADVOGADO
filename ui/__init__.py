"""
ui — Módulo de interface do usuário do Agente Jurídico IA.
"""
from ui.themes import COLORS, ETAPA_ICONS, get_css_theme, get_dark_css_theme, get_component_styles
from ui.components import (
    template_uploader,
    estilo_uploader,
    barra_progresso,
    cabecalho,
    card_info,
    badge_codigo,
    alerta_erro,
    checklist_visual,
)
from ui.pages import (
    render_triagem,
    render_confirmacao,
    render_coleta,
    render_contrato,
    render_geracao,
    render_revisao,
)

__all__ = [
    "COLORS",
    "ETAPA_ICONS",
    "get_css_theme",
    "get_dark_css_theme",
    "get_component_styles",
    "template_uploader",
    "estilo_uploader",
    "barra_progresso",
    "cabecalho",
    "card_info",
    "badge_codigo",
    "alerta_erro",
    "checklist_visual",
    "render_triagem",
    "render_confirmacao",
    "render_coleta",
    "render_contrato",
    "render_geracao",
    "render_revisao",
]
