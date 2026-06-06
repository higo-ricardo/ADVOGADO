"""
repository.py — Repositório de conhecimento jurídico.
Gerencia mapeamento de códigos de peças para arquivos e fornece contexto.
"""
from __future__ import annotations

from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from services.knowledge.loader import KnowledgeLoader

from infrastructure.exceptions import KnowledgeError


# Mapa código de peça → caminho relativo em knowledge/
MINUTA_POR_CODIGO: dict[str, str] = {
    # Domínio A
    "RPO": "imobiliarias/acao_reintegracao_posse.md",
    "MPO": "imobiliarias/acao_manutencao_posse.md",
    "IPR": "imobiliarias/acao_interdito_proibitorio.md",
    "IPO": "imobiliarias/acao_imissao_posse.md",
    "REI": "imobiliarias/acao_reivindicatoria.md",
    "CUS": "imobiliarias/contestacao_usucapiao.md",
    "ANU": "imobiliarias/acao_anulatoria_documento.md",
    "PAF": "imobiliarias/acao_passagem_forcada.md",
    "VIZ": "imobiliarias/vizinhanca_direito_construir.md",
    "DMT": "imobiliarias/acao_demarcacao_terras.md",
    # Domínio B
    "PI":  "consumeristas/minutas-consumeristas.md",
    "NEG": "consumeristas/minutas-consumeristas.md",
    "PSC": "consumeristas/minutas-consumeristas.md",
    "PSN": "consumeristas/minutas-consumeristas.md",
    "TEL": "consumeristas/minutas-consumeristas.md",
    "TRO": "consumeristas/minutas-consumeristas.md",
    "TRB": "consumeristas/minutas-consumeristas.md",
    "DIS": "consumeristas/minutas-consumeristas.md",
    "CEL": "consumeristas/minutas-consumeristas.md",
    "RPR": "consumeristas/minutas-consumeristas.md",
    "OBF": "consumeristas/minutas-consumeristas.md",
    "RI":  "consumeristas/minutas-consumeristas.md",
    "CR":  "consumeristas/minutas-consumeristas.md",
    "ED":  "consumeristas/minutas-consumeristas.md",
    "AI":  "consumeristas/minutas-consumeristas.md",
    # Domínio C
    "ATR": "civeis/minutas-civeis.md",
    "ALU": "civeis/cobranca_alugueis_rescisao.md",
    "REP": "civeis/replica_contestacao.md",
    # Domínio D
    "CHO": "documentos.md",
    "PRO": "intermediarias/procuracao_ad_judicia.md",
    "DHI": "intermediarias/declaracao_hipossuficiencia.md",
    "SUB": "intermediarias/substabelecimento.md",
    "HAB": "intermediarias/habilitacao_advogado.md",
    "ACO": "intermediarias/peticao_acordo.md",
    "ALV": "intermediarias/expedicao_alvara.md",
    "CPS": "intermediarias/cumprimento_sentenca.md",
    # Domínio F
    "NEP": "familia/minutas-familia.md",
    "INP": "familia/minutas-familia.md",
    "ALI": "familia/minutas-familia.md",
    "EXA": "familia/minutas-familia.md",
    "INV": "familia/minutas-familia.md",
    "OFA": "familia/minutas-familia.md",
    "UNE": "familia/minutas-familia.md",
    "INT": "familia/minutas-familia.md",
    "GUA": "familia/minutas-familia.md",
    "VIS": "familia/minutas-familia.md",
    "CUR": "familia/minutas-familia.md",
    "DIV": "familia/minutas-familia.md",
    # Domínio G
    "AP":  "remedios-constitucionais.md",
    "HC":  "remedios-constitucionais.md",
    "HD":  "remedios-constitucionais.md",
    "MS":  "remedios-constitucionais.md",
    # Domínio R
    "APE": "recursos-civeis.md",
    "AGI": "recursos-civeis.md",
    "EDC": "recursos-civeis.md",
    "AGR": "recursos-civeis.md",
    "RES": "recursos-civeis.md",
    "REX": "recursos-civeis.md",
}


class KnowledgeRepository:
    """
    Repositório de conhecimento jurídico.
    
    Responsabilidades:
    - Mapear códigos de peças para arquivos
    - Fornecer system prompts para advogado e estagiário
    - Montar contexto completo para geração de peças
    """
    
    def __init__(self, loader: "KnowledgeLoader | None" = None):
        """
        Inicializa o repositório.
        
        Args:
            loader: Carregador de conhecimento (opcional, cria um se não fornecido)
        """
        self.loader = loader or KnowledgeLoader()
    
    def get_system_advogado(self) -> str:
        """Retorna system prompt do advogado."""
        return self.loader.load("advogado.md")
    
    def get_system_estagiario(self) -> str:
        """Retorna system prompt do estagiário."""
        return self.loader.load("estagiario.md")
    
    def get_estilo(self) -> str:
        """Retorna estilo de redação jurídica."""
        return self.loader.load("estilo_juridico.md")
    
    def get_minuta_base(self) -> str:
        """Retorna minuta base (fragmentos de formatação)."""
        return self.loader.load("minuta-base.md")
    
    def get_fontes(self) -> str:
        """Retorna fontes normativas (STF, STJ, súmulas)."""
        base = self.loader.load("fontes.md")
        stf = self.loader.load("verbetesSTF.md")
        stj = self.loader.load("verbetesSTJ.md")
        sv = self.loader.load("sumulas-vinculantes.md")
        return f"{base}\n\n{stf}\n\n{stj}\n\n{sv}"
    
    def get_minuta_por_codigo(self, codigo: str) -> str:
        """
        Retorna minuta específica para um código de peça.
        
        Args:
            codigo: Código da peça (ex: "RPO", "NEG")
        
        Returns:
            Conteúdo da minuta
        """
        nome_arquivo = MINUTA_POR_CODIGO.get(codigo)
        if not nome_arquivo:
            raise KnowledgeError(f"Minuta não mapeada para código: {codigo}")
        return self.loader.load(nome_arquivo)
    
    def build_contexto_estagiario(self, codigo: str) -> str:
        """
        Monta contexto completo que o estagiário precisa para redigir.
        
        Args:
            codigo: Código da peça
        
        Returns:
            Contexto completo formatado
        """
        return "\n\n---\n\n".join([
            "# ESTILO DE REDAÇÃO\n" + self.get_estilo(),
            "# FRAGMENTOS DE FORMATAÇÃO\n" + self.get_minuta_base(),
            f"# MINUTAS — CÓDIGO {codigo}\n" + self.get_minuta_por_codigo(codigo),
            "# FUNDAMENTAÇÃO NORMATIVA\n" + self.get_fontes(),
        ])
    
    def get_all_mapeamentos(self) -> dict[str, str]:
        """
        Retorna todos os mapeamentos de códigos.
        
        Returns:
            Cópia do dicionário de mapeamentos
        """
        return MINUTA_POR_CODIGO.copy()
    
    def is_codigo_mapeado(self, codigo: str) -> bool:
        """
        Verifica se um código está mapeado.
        
        Args:
            codigo: Código da peça
        
        Returns:
            True se estiver mapeado
        """
        return codigo in MINUTA_POR_CODIGO
