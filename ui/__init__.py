"""
ui — Módulo de interface do usuário do Agente Jurídico IA.
"""
from ui.themes import COLORS, ETAPA_ICONS, get_component_styles, format_style_dict
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

__all__ = [
    "COLORS",
    "ETAPA_ICONS",
    "get_component_styles",
    "format_style_dict",
    "template_uploader",
    "estilo_uploader",
    "barra_progresso",
    "cabecalho",
    "card_info",
    "badge_codigo",
    "alerta_erro",
    "checklist_visual",
]
