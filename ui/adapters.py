"""
ui/adapters.py — Adaptadores entre UI (Streamlit) e Core.
"""
from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING, Generator

if TYPE_CHECKING:
    from services.llm.openrouter import OpenRouterProvider
    from services.rag.indexer import DocumentIndexer
    from services.rag.retriever import SemanticRetriever
    from services.rag.prompt_builder import RAGPromptBuilder
    from services.knowledge.loader import KnowledgeLoader
    from services.knowledge.repository import KnowledgeRepository

from infrastructure.config import config
from infrastructure.exceptions import AgentError, LLMError, RAGError


class UIAdapter:
    """
    Adaptador entre UI e serviços do Core.
    """

    def __init__(self):
        """Inicializa o adapter com todos os serviços necessários."""
        self._llm: "OpenRouterProvider | None" = None
        self._indexer: "DocumentIndexer | None" = None
        self._retriever: "SemanticRetriever | None" = None
        self._prompt_builder: "RAGPromptBuilder | None" = None
        self._knowledge_repo: "KnowledgeRepository | None" = None
        self._case_repo: Any | None = None
        self._document_repo: Any | None = None
        self._current_case_id: int | None = None

    @property
    def llm(self) -> "OpenRouterProvider":
        """Lazy loading do provedor LLM."""
        if self._llm is None:
            from services.llm.openrouter import OpenRouterProvider
            self._llm = OpenRouterProvider()
        return self._llm

    @property
    def indexer(self) -> "DocumentIndexer":
        """Lazy loading do indexador RAG."""
        if self._indexer is None:
            from services.rag.indexer import DocumentIndexer
            self._indexer = DocumentIndexer()
        return self._indexer

    @property
    def retriever(self) -> "SemanticRetriever":
        """Lazy loading do recuperador semântico."""
        if self._retriever is None:
            from services.rag.retriever import SemanticRetriever
            self._retriever = SemanticRetriever(self.indexer)
        return self._retriever

    @property
    def prompt_builder(self) -> "RAGPromptBuilder":
        """Lazy loading do construtor de prompts."""
        if self._prompt_builder is None:
            from services.rag.prompt_builder import RAGPromptBuilder
            self._prompt_builder = RAGPromptBuilder()
        return self._prompt_builder

    @property
    def knowledge_repo(self) -> "KnowledgeRepository":
        """Lazy loading do repositório de conhecimento."""
        if self._knowledge_repo is None:
            from services.knowledge.loader import KnowledgeLoader
            from services.knowledge.repository import KnowledgeRepository
            loader = KnowledgeLoader()
            self._knowledge_repo = KnowledgeRepository(loader)
        return self._knowledge_repo

    @property
    def case_repo(self) -> Any:
        """Lazy loading do repositório de casos."""
        if self._case_repo is None:
            from data.repositories.case_repository import CaseRepository
            self._case_repo = CaseRepository()
        return self._case_repo

    @property
    def document_repo(self) -> Any:
        """Lazy loading do repositório de documentos."""
        if self._document_repo is None:
            from data.repositories.document_repository import DocumentRepository
            self._document_repo = DocumentRepository()
        return self._document_repo

    def gerar_contrato(
        self,
        descricao_caso: str,
        dominio: str,
        dominio_nome: str,
        codigo: str,
        codigo_nome: str,
        modo: str,
        dados_coletados: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Gera contrato/briefing do caso e persiste no banco.
        """
        prompt = self.prompt_builder.build_contract_prompt(
            descricao_caso=descricao_caso,
            dominio=dominio,
            dominio_nome=dominio_nome,
            codigo=codigo,
            codigo_nome=codigo_nome,
            modo=modo,
            dados_coletados=dados_coletados,
        )

        messages = [
            {"role": "system", "content": "Você é um assistente jurídico especializado em criar briefings estruturados. Responda APENAS com JSON válido."},
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.llm.chat_completion(
                messages=messages,
                stream=False,
                max_tokens=config.MAX_TOKENS,
                temperature=0.3,
            )

            content = response.choices[0].message.content.strip()

            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()

            contrato = json.loads(content)

            # Persiste o caso no banco
            try:
                case = self.case_repo.create(
                    client_name=dados_coletados.get("autor", dados_coletados.get("requerente", "Nao informado")),
                    case_type=codigo,
                    description=descricao_caso,
                    metadata={
                        "dominio": dominio,
                        "dominio_nome": dominio_nome,
                        "codigo_nome": codigo_nome,
                        "modo": modo,
                        "dados_coletados": dados_coletados,
                        "contrato": contrato,
                    },
                )
                self._current_case_id = case.id
            except Exception as e:
                self._current_case_id = None

            return contrato

        except json.JSONDecodeError as exc:
            raise AgentError(f"Falha ao parsear JSON do contrato: {exc}")
        except Exception as exc:
            raise AgentError(f"Erro ao gerar contrato: {exc}")

    def estagiario_redigir(
        self,
        contrato: dict[str, Any],
        codigo: str,
    ) -> Generator[str, None, None]:
        """
        Gera peça jurídica com streaming (papel do estagiário),
        e persiste ao final.
        """
        peca_completa = ""

        try:
            if not self.indexer.is_indexed:
                self._indexar_documentos(codigo)

            query = f"{contrato.get('escopo', '')} {codigo}"
            trechos = self.retriever.search(query, top_k=config.RAG_TOP_K)

            contexto_estagiario = self.knowledge_repo.build_contexto_estagiario(codigo)

            prompt = self.prompt_builder.build_document_prompt(
                descricao_caso=contrato.get("dados", {}).get("descricao_caso", ""),
                dominio=contrato.get("dominio", "").split(" — ")[0].strip(),
                dominio_nome=contrato.get("dominio", "").split(" — ")[-1].strip(),
                codigo=codigo,
                codigo_nome=contrato.get("tipo_peca", ""),
                modo=contrato.get("modo", "integrado"),
                dados_coletados=contrato.get("dados", {}),
                context_trechos=trechos,
            )

            system_prompt = self.knowledge_repo.get_system_estagiario()

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            for chunk in self.llm.chat_completion_stream(
                messages=messages,
                max_tokens=config.MAX_TOKENS,
                temperature=0.7,
            ):
                peca_completa += chunk
                yield chunk

            # Persiste o documento no banco após a geração completa
            if peca_completa.strip() and self._current_case_id:
                try:
                    self.document_repo.create(
                        case_id=self._current_case_id,
                        document_type="peca_processual",
                        title=f"Peca {codigo} - v1",
                        content=peca_completa,
                        author_ai_model=self.llm.model if hasattr(self.llm, 'model') else "openrouter",
                    )
                except Exception:
                    pass

        except Exception as exc:
            raise AgentError(f"Erro na redação da peça: {exc}")

    def advogado_delta(
        self,
        peca_atual: str,
        instrucao_delta: str,
        contrato: dict[str, Any],
    ) -> Generator[str, None, None]:
        """
        Aplica modificações (delta) em uma peça existente,
        e persiste a nova versão ao final.
        """
        peca_completa = ""

        try:
            prompt = self.prompt_builder.build_delta_prompt(
                peca_atual=peca_atual,
                instrucao_delta=instrucao_delta,
                contrato=contrato,
            )

            system_prompt = self.knowledge_repo.get_system_advogado()

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            for chunk in self.llm.chat_completion_stream(
                messages=messages,
                max_tokens=config.MAX_TOKENS,
                temperature=0.5,
            ):
                peca_completa += chunk
                yield chunk

            # Persiste nova versão do documento
            if peca_completa.strip() and self._current_case_id:
                try:
                    self.document_repo.create(
                        case_id=self._current_case_id,
                        document_type="peca_processual",
                        title=f"Peca {contrato.get('tipo_peca', '')} - delta",
                        content=peca_completa,
                        author_ai_model=self.llm.model if hasattr(self.llm, 'model') else "openrouter",
                    )
                except Exception:
                    pass

        except Exception as exc:
            raise AgentError(f"Erro ao aplicar delta: {exc}")

    def _indexar_documentos(self, codigo: str) -> int:
        documentos: dict[str, str] = {}

        try:
            minuta = self.knowledge_repo.get_minuta_por_codigo(codigo)
            documentos[f"minuta_{codigo}"] = minuta
        except Exception:
            pass

        try:
            documentos["estilo"] = self.knowledge_repo.get_estilo()
            documentos["formatacao"] = self.knowledge_repo.get_minuta_base()
        except Exception:
            pass

        try:
            documentos["fontes"] = self.knowledge_repo.get_fontes()
        except Exception:
            pass

        return self.indexer.index_documents(documentos)

    def reiniciar_index(self) -> None:
        """Reinicia o índice RAG."""
        self.indexer.reset()
        if self._retriever is not None:
            self._retriever = None


# Instância global para uso compartilhado
_adapter: UIAdapter | None = None


def get_adapter() -> UIAdapter:
    """Obtém ou cria instância singleton do adapter."""
    global _adapter
    if _adapter is None:
        _adapter = UIAdapter()
    return _adapter


__all__ = ["UIAdapter", "get_adapter"]


# ============================================================================
# State Machine Adapters (para integração com Streamlit)
# ============================================================================

def get_state_machine() -> Any:
    """
    Obtém ou cria instância da State Machine no session_state.
    """
    import streamlit as st

    if "state_machine" not in st.session_state:
        from core.state_machine import StateMachine
        st.session_state.state_machine = StateMachine()

    return st.session_state.state_machine


def save_state_machine(state_machine: Any) -> None:
    """
    Salva a State Machine no session_state.
    """
    import streamlit as st
    st.session_state.state_machine = state_machine
