"""
state_machine.py — State machine testável do agente jurídico.
Gerencia as 6 etapas do fluxo e todos os dados de sessão.

Diferente do state.py original, este módulo NÃO depende do Streamlit,
permitindo testes unitários e uso em outros contextos (CLI, API, etc.).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Etapa(str, Enum):
    """Etapas do fluxo do agente."""
    TRIAGEM = "triagem"           # 1. Usuario descreve o caso
    CONFIRMACAO = "confirmacao"   # 2. Confirmar dominio + codigo da peca
    COLETA = "coleta"             # 3. Preencher dados faltantes
    CONTRATO = "contrato"         # 4. Revisar contrato gerado
    GERACAO = "geracao"           # 5. Geracao da peça (streaming)
    REVISAO = "revisao"           # 6. Revisao + aprovacao + download


ETAPA_LABEL: dict[Etapa, str] = {
    Etapa.TRIAGEM:     "1. Descrever o caso",
    Etapa.CONFIRMACAO: "2. Confirmar peça",
    Etapa.COLETA:      "3. Dados do caso",
    Etapa.CONTRATO:    "4. Revisar briefing",
    Etapa.GERACAO:     "5. Gerando peça",
    Etapa.REVISAO:     "6. Revisao e download",
}


@dataclass
class AgentState:
    """
    Estado do agente jurídico.
    
    Esta classe é pura (sem dependências externas) e pode ser:
    - Serializada/desserializada
    - Testada unitariamente
    - Usada em qualquer contexto (Streamlit, CLI, API, etc.)
    """
    etapa: Etapa = Etapa.TRIAGEM
    descricao_caso: str = ""
    dominio: str | None = None
    dominio_nome: str | None = None
    codigo_peca: str | None = None
    codigo_nome: str | None = None
    modo: str | None = None
    dados_coletados: dict[str, Any] = field(default_factory=dict)
    contrato: dict[str, Any] = field(default_factory=dict)
    peca_gerada: str = ""
    checklist: list[str] = field(default_factory=list)
    historico_advogado: list[dict] = field(default_factory=list)
    historico_estagiario: list[dict] = field(default_factory=list)
    erro: str | None = None
    
    def avancar(self, proxima: Etapa) -> None:
        """Avança para a próxima etapa."""
        self.etapa = proxima
        self.erro = None
    
    def reiniciar(self) -> None:
        """Reinicia todo o estado para os valores padrão."""
        self.__init__()
    
    def etapa_idx(self) -> int:
        """Retorna o índice numérico da etapa atual."""
        return list(Etapa).index(self.etapa)
    
    def to_dict(self) -> dict[str, Any]:
        """Serializa o estado para um dicionário."""
        return {
            "etapa": self.etapa.value,
            "descricao_caso": self.descricao_caso,
            "dominio": self.dominio,
            "dominio_nome": self.dominio_nome,
            "codigo_peca": self.codigo_peca,
            "codigo_nome": self.codigo_nome,
            "modo": self.modo,
            "dados_coletados": self.dados_coletados,
            "contrato": self.contrato,
            "peca_gerada": self.peca_gerada,
            "checklist": self.checklist,
            "historico_advogado": self.historico_advogado,
            "historico_estagiario": self.historico_estagiario,
            "erro": self.erro,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentState":
        """Desserializa o estado a partir de um dicionário."""
        data = data.copy()
        if "etapa" in data and isinstance(data["etapa"], str):
            data["etapa"] = Etapa(data["etapa"])
        return cls(**data)


class StateMachine:
    """
    Gerenciador de estado do agente.
    
    Fornece uma interface conveniente para manipular o AgentState,
    com validações e transições seguras.
    """
    
    def __init__(self, state: AgentState | None = None):
        self.state = state or AgentState()
    
    @property
    def etapa_atual(self) -> Etapa:
        return self.state.etapa
    
    @property
    def etapa_label(self) -> str:
        return ETAPA_LABEL.get(self.etapa_atual, "Desconhecido")
    
    def avancar(self, proxima: Etapa) -> None:
        """Avança para uma nova etapa."""
        self.state.avancar(proxima)
    
    def reiniciar(self) -> None:
        """Reinicia o estado."""
        self.state.reiniciar()
    
    def validar_transicao(self, origem: Etapa, destino: Etapa) -> bool:
        """
        Valida se a transição entre etapas é permitida.
        
        Regras:
        - Só pode avançar uma etapa por vez (exceto reinício)
        - Não pode pular etapas
        """
        if destino == Etapa.TRIAGEM:
            return True  # Sempre pode reiniciar
        
        idx_origem = list(Etapa).index(origem)
        idx_destino = list(Etapa).index(destino)
        
        # Só permite avançar uma etapa ou voltar
        return abs(idx_destino - idx_origem) <= 1
    
    def get(self, chave: str, default: Any = None) -> Any:
        """Obtém um valor do estado."""
        return getattr(self.state, chave, default)
    
    def set(self, chave: str, valor: Any) -> None:
        """Define um valor no estado."""
        if hasattr(self.state, chave):
            setattr(self.state, chave, valor)
        else:
            raise AttributeError(f"Estado não possui atributo: {chave}")
    
    def to_dict(self) -> dict[str, Any]:
        """Serializa o estado completo."""
        return self.state.to_dict()
    
    def from_dict(self, data: dict[str, Any]) -> None:
        """Carrega estado a partir de dicionário."""
        self.state = AgentState.from_dict(data)
