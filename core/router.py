"""
router.py — Roteamento determinístico baseado em configuração.
Este módulo substitui o router.py original com dados externalizados.

Agora os dados de roteamento estão em data/router_config.yaml,
facilitando manutenção e extensão sem modificar código.
"""
from __future__ import annotations

import yaml
from pathlib import Path
from typing import Optional


class RouterConfig:
    """Carrega e fornece acesso à configuração de roteamento."""
    
    def __init__(self, config_path: str | None = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "data" / "router_config.yaml"
        
        self.config_path = Path(config_path)
        self._config: dict = {}
        self._load()
    
    def _load(self) -> None:
        """Carrega configuração do YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuração de roteamento não encontrada: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)
    
    @property
    def keywords(self) -> dict[str, list]:
        """Retorna mapeamento de keywords → [dominio_id, dominio_nome]."""
        return self._config.get("dominios", {}).get("keywords", {})
    
    @property
    def codigos_por_dominio(self) -> dict[str, list[list[str]]]:
        """Retorna códigos disponíveis por domínio."""
        return self._config.get("codigos_por_dominio", {})
    
    @property
    def codigos_autonomos(self) -> set[str]:
        """Retorna conjunto de códigos autônomos."""
        return set(self._config.get("codigos_autonomos", []))


# Instância global (lazy loading)
_config: RouterConfig | None = None


def _get_config() -> RouterConfig:
    """Obtém ou cria instância da configuração."""
    global _config
    if _config is None:
        _config = RouterConfig()
    return _config


def detectar_dominio(texto: str) -> tuple[str, str] | None:
    """
    Retorna (id_dominio, nome) se encontrar keyword no texto.
    
    Args:
        texto: Texto da descrição do caso
    
    Returns:
        Tuple (dominio_id, dominio_nome) ou None se não encontrar
    """
    config = _get_config()
    texto_lower = texto.lower()
    
    for kw, valor in config.keywords.items():
        if kw in texto_lower:
            return valor[0], valor[1]
    
    return None


def codigos_do_dominio(dom_id: str) -> list[tuple[str, str]]:
    """
    Retorna lista de códigos disponíveis para um domínio.
    
    Args:
        dom_id: ID do domínio (A, B, C, etc.)
    
    Returns:
        Lista de tuples [(codigo, nome), ...]
    """
    config = _get_config()
    codigos = config.codigos_por_dominio.get(dom_id, [])
    return [(c[0], c[1]) for c in codigos]


def campos_do_codigo(codigo: str) -> list[dict]:
    """
    Retorna campos obrigatórios para um código de peça.
    
    Nota: Esta função mantém os campos hardcoded temporariamente.
    Futuramente os campos também serão externalizados para YAML.
    """
    # Campos obrigatórios por código de peça (mantido do original)
    CAMPOS_OBRIGATORIOS: dict[str, list[dict]] = {
        # --- DOMÍNIO A ---
        "RPO": [
            {"id": "autor", "label": "Nome completo do autor", "tipo": "text"},
            {"id": "reu",   "label": "Nome completo do réu",   "tipo": "text"},
            {"id": "imovel","label": "Descrição do imóvel",    "tipo": "textarea"},
            {"id": "data_esbulho","label": "Data do esbulho",  "tipo": "text"},
            {"id": "forca", "label": "Força nova (<1 ano) ou velha?", "tipo": "select",
             "opcoes": ["Nova (menos de 1 ano e 1 dia)", "Velha (1 ano e 1 dia ou mais)"]},
        ],
        "MPO": [
            {"id": "autor", "label": "Nome completo do autor", "tipo": "text"},
            {"id": "reu",   "label": "Nome completo do réu",   "tipo": "text"},
            {"id": "imovel","label": "Descrição do imóvel",    "tipo": "textarea"},
            {"id": "atos_turbacao","label": "Descreva os atos de turbação", "tipo": "textarea"},
        ],
        # --- DOMÍNIO B ---
        "NEG": [
            {"id": "autor",  "label": "Nome completo do autor",     "tipo": "text"},
            {"id": "cpf",    "label": "CPF do autor",                "tipo": "text"},
            {"id": "reu",    "label": "Nome do réu (credor/empresa)","tipo": "text"},
            {"id": "valor",  "label": "Valor negativado (R$)",       "tipo": "text"},
            {"id": "data",   "label": "Data da negativação",         "tipo": "text"},
            {"id": "fatos",  "label": "Descreva brevemente os fatos","tipo": "textarea"},
        ],
        "PSC": [
            {"id": "autor",  "label": "Nome completo do autor",     "tipo": "text"},
            {"id": "plano",  "label": "Nome da operadora",           "tipo": "text"},
            {"id": "fatos",  "label": "Descreva o cancelamento indevido", "tipo": "textarea"},
        ],
        "PSN": [
            {"id": "autor",      "label": "Nome completo do autor",         "tipo": "text"},
            {"id": "plano",      "label": "Nome da operadora",               "tipo": "text"},
            {"id": "procedimento","label": "Procedimento/cobertura negada",  "tipo": "textarea"},
            {"id": "justificativa","label": "Justificativa dada pela operadora","tipo": "textarea"},
        ],
        "TEL": [
            {"id": "autor",  "label": "Nome completo do autor",     "tipo": "text"},
            {"id": "empresa","label": "Nome da operadora",           "tipo": "text"},
            {"id": "fatos",  "label": "Descreva o problema (bloqueio, cobrança, etc.)","tipo": "textarea"},
        ],
        # --- DOMÍNIO C ---
        "ATR": [
            {"id": "autor",   "label": "Nome completo do autor",    "tipo": "text"},
            {"id": "reu",     "label": "Nome completo do réu",      "tipo": "text"},
            {"id": "data",    "label": "Data do acidente",          "tipo": "text"},
            {"id": "local",   "label": "Local do acidente",         "tipo": "text"},
            {"id": "danos",   "label": "Descreva os danos (veículo, físicos, etc.)", "tipo": "textarea"},
            {"id": "bo",      "label": "Número do BO (se houver)",  "tipo": "text"},
        ],
        "ALU": [
            {"id": "locador", "label": "Nome do locador",           "tipo": "text"},
            {"id": "locatario","label": "Nome do locatário",        "tipo": "text"},
            {"id": "imovel",  "label": "Endereço do imóvel",        "tipo": "textarea"},
            {"id": "valor_aluguel","label": "Valor mensal do aluguel (R$)","tipo": "text"},
            {"id": "meses_devidos","label": "Quantidade de meses em débito","tipo": "text"},
        ],
        "REP": [
            {"id": "autor",        "label": "Nome do autor",            "tipo": "text"},
            {"id": "reu",          "label": "Nome do réu",              "tipo": "text"},
            {"id": "processo",     "label": "Número do processo",       "tipo": "text"},
            {"id": "preliminares", "label": "Preliminares levantadas pelo réu (se houver)", "tipo": "textarea"},
            {"id": "teses_merito", "label": "Teses de mérito da contestação (resumidas)", "tipo": "textarea"},
        ],
        # --- DOMÍNIO D ---
        "CHO": [
            {"id": "advogado",  "label": "Nome completo do advogado",   "tipo": "text"},
            {"id": "oab",       "label": "OAB (número e estado)",        "tipo": "text"},
            {"id": "cliente",   "label": "Nome completo do cliente",     "tipo": "text"},
            {"id": "cpf_cliente","label": "CPF do cliente",             "tipo": "text"},
            {"id": "objeto",    "label": "Objeto dos honorários (descreva a causa)", "tipo": "textarea"},
            {"id": "valor",     "label": "Valor dos honorários (R$) ou percentual","tipo": "text"},
        ],
        "PRO": [
            {"id": "outorgante", "label": "Nome completo do outorgante","tipo": "text"},
            {"id": "cpf",        "label": "CPF do outorgante",          "tipo": "text"},
            {"id": "advogado",   "label": "Nome completo do advogado",  "tipo": "text"},
            {"id": "oab",        "label": "OAB (número e estado)",      "tipo": "text"},
            {"id": "objeto",     "label": "Finalidade da procuração",   "tipo": "textarea"},
        ],
        "DHI": [
            {"id": "requerente","label": "Nome completo do requerente", "tipo": "text"},
            {"id": "cpf",       "label": "CPF do requerente",           "tipo": "text"},
            {"id": "renda",     "label": "Renda mensal aproximada (R$)","tipo": "text"},
        ],
        "ALV": [
            {"id": "requerente","label": "Nome do requerente",          "tipo": "text"},
            {"id": "processo",  "label": "Número do processo",          "tipo": "text"},
            {"id": "valor",     "label": "Valor a ser levantado (R$)",  "tipo": "text"},
            {"id": "banco",     "label": "Banco, agência e conta corrente","tipo": "text"},
            {"id": "cpf",       "label": "CPF do titular da conta",     "tipo": "text"},
        ],
        "CPS": [
            {"id": "exequente", "label": "Nome do exequente",           "tipo": "text"},
            {"id": "executado",  "label": "Nome do executado",          "tipo": "text"},
            {"id": "processo",   "label": "Número do processo",         "tipo": "text"},
            {"id": "valor_condenacao","label": "Valor da condenação (R$)","tipo": "text"},
            {"id": "memoria_calculo","label": "Memória de cálculo atualizada (cole aqui)", "tipo": "textarea"},
        ],
        # --- DOMÍNIO F ---
        "ALI": [
            {"id": "alimentando","label": "Nome do alimentando",        "tipo": "text"},
            {"id": "alimentante","label": "Nome do alimentante",        "tipo": "text"},
            {"id": "necessidade","label": "Descreva a necessidade (despesas mensais)", "tipo": "textarea"},
            {"id": "possibilidade","label": "Descreva a possibilidade do alimentante","tipo": "textarea"},
            {"id": "valor_pedido","label": "Valor dos alimentos pleiteados (R$ ou SM)","tipo": "text"},
        ],
        "DIV": [
            {"id": "conjuge1", "label": "Nome do cônjuge 1",            "tipo": "text"},
            {"id": "conjuge2", "label": "Nome do cônjuge 2",            "tipo": "text"},
            {"id": "casamento","label": "Data do casamento",            "tipo": "text"},
            {"id": "regime",   "label": "Regime de bens",               "tipo": "select",
             "opcoes": ["Comunhão parcial de bens","Comunhão universal de bens","Separação de bens","Participação final nos aquestos"]},
            {"id": "filhos",   "label": "Há filhos menores? Informe nome(s) e idade(s)", "tipo": "textarea"},
            {"id": "bens",     "label": "Bens a partilhar (se houver)", "tipo": "textarea"},
        ],
        # --- DOMÍNIO G ---
        "HC": [
            {"id": "paciente",    "label": "Nome do paciente",          "tipo": "text"},
            {"id": "autoridade",  "label": "Autoridade coatora",        "tipo": "text"},
            {"id": "especie",     "label": "Espécie do HC", "tipo": "select",
             "opcoes": ["Liberatório (soltar preso)","Preventivo (evitar prisão)","Trancamento de ação penal"]},
            {"id": "fatos",       "label": "Descreva o constrangimento ilegal", "tipo": "textarea"},
        ],
        "MS": [
            {"id": "impetrante",  "label": "Nome do impetrante",        "tipo": "text"},
            {"id": "autoridade",  "label": "Autoridade coatora",        "tipo": "text"},
            {"id": "ato_coator",  "label": "Descreva o ato coator",     "tipo": "textarea"},
            {"id": "direito",     "label": "Direito líquido e certo violado", "tipo": "textarea"},
        ],
        # --- DOMÍNIO R ---
        "APE": [
            {"id": "apelante",  "label": "Nome do apelante",            "tipo": "text"},
            {"id": "apelado",   "label": "Nome do apelado",             "tipo": "text"},
            {"id": "processo",  "label": "Número do processo",          "tipo": "text"},
            {"id": "sentenca",  "label": "Resumo da sentença recorrida","tipo": "textarea"},
            {"id": "teses",     "label": "Teses do recurso",            "tipo": "textarea"},
        ],
    }
    
    # Fallback genérico para códigos sem campos mapeados
    CAMPOS_GENERICOS = [
        {"id": "autor",  "label": "Nome completo do autor / requerente", "tipo": "text"},
        {"id": "reu",    "label": "Nome completo do réu / requerido",    "tipo": "text"},
        {"id": "fatos",  "label": "Descreva os fatos do caso",           "tipo": "textarea"},
        {"id": "pedido", "label": "O que deseja pedir ao juiz?",         "tipo": "textarea"},
    ]
    
    return CAMPOS_OBRIGATORIOS.get(codigo, CAMPOS_GENERICOS)


def is_autonomo(codigo: str) -> bool:
    """
    Verifica se um código é autônomo (não precisa de handoff).
    
    Args:
        codigo: Código da peça
    
    Returns:
        True se for autônomo, False caso contrário
    """
    config = _get_config()
    return codigo in config.codigos_autonomos


# Compatibilidade com o módulo original
__all__ = [
    "detectar_dominio",
    "codigos_do_dominio",
    "campos_do_codigo",
    "is_autonomo",
    "RouterConfig",
]
