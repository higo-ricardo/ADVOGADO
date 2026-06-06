"""
src/domain/dtos/__init__.py — Data Transfer Objects (DTOs) para comunicação entre camadas.

Estes DTOs definem contratos rígidos de entrada e saída entre:
- UI → Camada de Aplicação
- Camada de Aplicação → Serviços
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ============================================================================
# DTOs de Requisição (Input)
# ============================================================================

@dataclass
class SubmitLegalQueryRequest:
    """Requisição para submissão de consulta jurídica."""
    descricao_caso: str
    modo: str = "integrado"


@dataclass
class ConfirmPieceRequest:
    """Requisição para confirmação de peça."""
    dominio: str
    dominio_nome: str
    codigo_peca: str
    codigo_nome: str
    modo: str


@dataclass
class CollectDataRequest:
    """Requisição para coleta de dados."""
    dados_coletados: dict[str, Any]


@dataclass
class GenerateDocumentRequest:
    """Requisição para geração de documento."""
    contrato: dict[str, Any]
    codigo_peca: str


@dataclass
class ApplyDeltaRequest:
    """Requisição para aplicação de modificações."""
    peca_atual: str
    instrucao_delta: str
    contrato: dict[str, Any]


@dataclass
class ResetStateRequest:
    """Requisição para resetar o estado da sessão."""
    session_id: str = "default"


# ============================================================================
# DTOs de Resposta (Output)
# ============================================================================

@dataclass
class TriagemResponse:
    """Resposta da triagem."""
    sucesso: bool
    dominio: str | None = None
    dominio_nome: str | None = None
    mensagem: str = ""
    erro: str | None = None


@dataclass
class ConfirmacaoResponse:
    """Resposta da confirmação."""
    sucesso: bool
    codigos_disponiveis: list[tuple[str, str]] = field(default_factory=list)
    mensagem: str = ""
    erro: str | None = None


@dataclass
class ContratoResponse:
    """Resposta da geração de contrato."""
    sucesso: bool
    contrato: dict[str, Any] = field(default_factory=dict)
    mensagem: str = ""
    erro: str | None = None


@dataclass
class DocumentChunkResponse:
    """Resposta de chunk de documento (streaming)."""
    chunk: str
    completo: bool = False
    erro: str | None = None


@dataclass
class DocumentGenerationResponse:
    """Resposta da geração de documento."""
    sucesso: bool
    peca_gerada: str = ""
    checklist: list[str] = field(default_factory=list)
    mensagem: str = ""
    erro: str | None = None


@dataclass
class DeltaResponse:
    """Resposta da aplicação de delta."""
    sucesso: bool
    peca_modificada: str = ""
    mensagem: str = ""
    erro: str | None = None


# ============================================================================
# DTOs de Estado (State)
# ============================================================================

@dataclass
class AppStateDTO:
    """DTO para estado da aplicação."""
    etapa: str
    etapa_label: str
    descricao_caso: str
    dominio: str | None
    dominio_nome: str | None
    codigo_peca: str | None
    codigo_nome: str | None
    modo: str | None
    dados_coletados: dict[str, Any]
    contrato: dict[str, Any]
    peca_gerada: str
    checklist: list[str]
    erro: str | None
    
    @classmethod
    def from_state_dict(cls, state_dict: dict[str, Any]) -> "AppStateDTO":
        """Cria DTO a partir de dicionário de estado."""
        return cls(
            etapa=state_dict.get("etapa", "triagem"),
            etapa_label=state_dict.get("etapa_label", ""),
            descricao_caso=state_dict.get("descricao_caso", ""),
            dominio=state_dict.get("dominio"),
            dominio_nome=state_dict.get("dominio_nome"),
            codigo_peca=state_dict.get("codigo_peca"),
            codigo_nome=state_dict.get("codigo_nome"),
            modo=state_dict.get("modo"),
            dados_coletados=state_dict.get("dados_coletados", {}),
            contrato=state_dict.get("contrato", {}),
            peca_gerada=state_dict.get("peca_gerada", ""),
            checklist=state_dict.get("checklist", []),
            erro=state_dict.get("erro"),
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Converte DTO para dicionário."""
        return {
            "etapa": self.etapa,
            "etapa_label": self.etapa_label,
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
            "erro": self.erro,
        }


# ============================================================================
# DTOs de Erro
# ============================================================================

@dataclass
class ErrorDTO:
    """DTO padronizado para erros."""
    codigo: str
    mensagem: str
    detalhes: str | None = None
    recuperavel: bool = True
