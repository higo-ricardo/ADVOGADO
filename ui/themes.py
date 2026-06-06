"""
ui/themes.py — Temas e estilos CSS centralizados para o Agente Jurídico.
Separa toda a estilização da lógica de componentes.
"""
from typing import TypedDict


class ThemeColors(TypedDict):
    """Tipagem para cores do tema."""
    primary: str
    secondary: str
    success: str
    warning: str
    error: str
    info: str
    background_light: str
    background_dark: str
    text_light: str
    text_dark: str
    border: str


# Paleta de cores jurídica profissional
COLORS: ThemeColors = {
    "primary": "#1e3a8a",        # Azul jurídico profundo
    "secondary": "#3b82f6",      # Azul secundário
    "success": "#10b981",        # Verde sucesso
    "warning": "#f59e0b",        # Âmbar alerta
    "error": "#ef4444",          # Vermelho erro
    "info": "#06b6d4",           # Ciano informação
    "background_light": "#ffffff",
    "background_dark": "#1e293b",
    "text_light": "#1e293b",
    "text_dark": "#f8fafc",
    "border": "#e2e8f0",
}

# Ícones visuais para as 6 etapas
ETAPA_ICONS = ["📁", "✓", "📝", "📋", "✍", "🔍"]

# CSS Base para componentes
CSS_BASE = """
<style>
/* Reset básico */
.stApp {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Cards informativos */
.info-card {
    border-left: 4px solid {primary};
    padding: 16px 20px;
    background: {bg};
    border-radius: 8px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

/* Badges */
.badge {
    display: inline-block;
    background: {primary};
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 13px;
    margin-bottom: 12px;
}

/* Alertas */
.alert-error {
    background: #fef2f2;
    border-left: 4px solid {error};
    padding: 12px 16px;
    border-radius: 8px;
    margin: 12px 0;
}

.alert-warning {
    background: #fffbeb;
    border-left: 4px solid {warning};
    padding: 12px 16px;
    border-radius: 8px;
    margin: 12px 0;
}

.alert-success {
    background: #ecfdf5;
    border-left: 4px solid {success};
    padding: 12px 16px;
    border-radius: 8px;
    margin: 12px 0;
}

/* Checklist */
.checklist-item {
    margin: 6px 0;
    padding: 4px 0;
}

.checklist-icon {
    color: {success};
    font-weight: bold;
}

/* Cabeçalho */
.header-title {
    font-size: 28px;
    font-weight: 700;
    color: {primary};
}

.header-subtitle {
    font-size: 14px;
    color: #64748b;
}

/* Progresso */
.progress-step {
    display: flex;
    align-items: center;
    justify-content: center;
    background: {bg_step};
    color: {color_step};
    width: 32px;
    height: 32px;
    border-radius: 50%;
    font-weight: bold;
    margin: auto;
    font-size: 14px;
}

.progress-label {
    text-align: center;
    font-size: 10px;
    margin-top: 4px;
    color: #64748b;
}

/* Status online */
.status-online {
    color: {success};
    font-size: 12px;
}
</style>
"""


def get_css_theme(primary_color: str | None = None) -> str:
    """
    Retorna o CSS completo com as cores do tema.
    
    Args:
        primary_color: Cor primária personalizada (opcional)
    
    Returns:
        String com CSS completo
    """
    colors = COLORS.copy()
    if primary_color:
        colors["primary"] = primary_color
    
    return CSS_BASE.format(
        primary=colors["primary"],
        secondary=colors["secondary"],
        success=colors["success"],
        warning=colors["warning"],
        error=colors["error"],
        info=colors["info"],
        bg=colors["background_light"],
        bg_step="#e2e8f0",
        color_step=colors["primary"],
    )


def get_dark_css_theme() -> str:
    """Retorna CSS adaptado para modo escuro."""
    colors = COLORS
    
    dark_css = """
<style>
/* Modo escuro */
.dark-mode .info-card {
    background: {bg_dark};
    color: {text_dark};
}

.dark-mode .progress-step-inactive {
    background: #334155;
}

.dark-mode .progress-label-inactive {
    color: #94a3b8;
}

.dark-mode .badge {
    background: {primary};
    color: white;
}
</style>
"""
    
    return dark_css.format(
        bg_dark=colors["background_dark"],
        text_dark=colors["text_dark"],
        primary=colors["primary"],
    )


def get_component_styles(component_name: str) -> dict:
    """
    Retorna estilos específicos para um componente.
    
    Args:
        component_name: Nome do componente ('card', 'badge', 'alert', etc.)
    
    Returns:
        Dicionário com estilos do componente
    """
    styles = {
        "card": {
            "border_left": f"4px solid {COLORS['primary']}",
            "padding": "16px 20px",
            "background": COLORS["background_light"],
            "border_radius": "8px",
            "margin_bottom": "16px",
            "box_shadow": "0 1px 3px rgba(0,0,0,0.08)",
        },
        "card_dark": {
            "border_left": f"4px solid {COLORS['primary']}",
            "padding": "16px 20px",
            "background": COLORS["background_dark"],
            "border_radius": "8px",
            "margin_bottom": "16px",
            "box_shadow": "0 1px 3px rgba(0,0,0,0.2)",
        },
        "badge": {
            "display": "inline-block",
            "background": COLORS["primary"],
            "color": "white",
            "padding": "6px 14px",
            "border_radius": "20px",
            "font_weight": "600",
            "font_size": "13px",
            "margin_bottom": "12px",
        },
        "alert_error": {
            "background": "#fef2f2",
            "border_left": f"4px solid {COLORS['error']}",
            "padding": "12px 16px",
            "border_radius": "8px",
            "margin": "12px 0",
        },
        "alert_warning": {
            "background": "#fffbeb",
            "border_left": f"4px solid {COLORS['warning']}",
            "padding": "12px 16px",
            "border_radius": "8px",
            "margin": "12px 0",
        },
        "alert_success": {
            "background": "#ecfdf5",
            "border_left": f"4px solid {COLORS['success']}",
            "padding": "12px 16px",
            "border_radius": "8px",
            "margin": "12px 0",
        },
        "checklist_item": {
            "margin": "6px 0",
            "padding": "4px 0",
        },
        "progress_step_active": {
            "background": COLORS["primary"],
            "color": "white",
            "width": "32px",
            "height": "32px",
            "border_radius": "50%",
            "font_weight": "bold",
            "font_size": "14px",
        },
        "progress_step_inactive": {
            "background": "#e2e8f0",
            "color": COLORS["primary"],
            "width": "32px",
            "height": "32px",
            "border_radius": "50%",
            "font_weight": "bold",
            "font_size": "14px",
        },
    }
    
    return styles.get(component_name, {})


def format_style_dict(styles: dict) -> str:
    """
    Converte dicionário de estilos para string CSS inline.
    
    Args:
        styles: Dicionário com propriedades CSS
    
    Returns:
        String no formato CSS inline
    """
    css_parts = []
    for key, value in styles.items():
        # Converte snake_case para kebab-case
        css_key = key.replace("_", "-")
        css_parts.append(f"{css_key}: {value}")
    
    return "; ".join(css_parts)
