"""
src/application/app_facade.py — Fachada da Aplicação.

Fornece uma interface unificada e simplificada para a UI acessar
todos os casos de uso, sem precisar conhecer detalhes de implementação.
"""
from __future__ import annotations

from typing import Any, Generator

from core.state_machine import StateMachine
from services.llm.openrouter import OpenRouterProvider
from services.rag.indexer import DocumentIndexer
from services.rag.retriever import SemanticRetriever
from services.rag.prompt_builder import RAGPromptBuilder
from services.knowledge.loader import KnowledgeLoader
from services.knowledge.repository import KnowledgeRepository

from src.domain.dtos import (
    SubmitLegalQueryRequest,
    TriagemResponse,
    ConfirmPieceRequest,
    ConfirmacaoResponse,
    CollectDataRequest,
    ContratoResponse,
    ApplyDeltaRequest,
    AppStateDTO,
)
from src.application.use_cases import (
    SubmitLegalQueryUseCase,
    ConfirmPieceUseCase,
    CollectDataUseCase,
    GenerateContractUseCase,
    GenerateDocumentUseCase,
    ApplyDeltaUseCase,
    ResetStateUseCase,
)


class AppFacade:
    """
    Fachada para a camada de aplicação.
    
    Esta classe fornece:
    - Interface simplificada para todos os casos de uso
    - Gerenciamento de dependências dos serviços
    - Tradução entre DTOs e estado interno
    
    A UI deve usar APENAS esta classe, nunca acessando serviços diretamente.
    """
    
    def __init__(
        self,
        state_machine: StateMachine,
        llm_provider: OpenRouterProvider | None = None,
        indexer: DocumentIndexer | None = None,
        retriever: SemanticRetriever | None = None,
        prompt_builder: RAGPromptBuilder | None = None,
        knowledge_repo: KnowledgeRepository | None = None,
    ):
        """
        Inicializa a fachada com todas as dependências.
        
        Args:
            state_machine: Instância da máquina de estados
            llm_provider: Provedor LLM (cria se None)
            indexer: Indexador de documentos (cria se None)
            retriever: Recuperador semântico (cria se None)
            prompt_builder: Construtor de prompts (cria se None)
            knowledge_repo: Repositório de conhecimento (cria se None)
        """
        self.state_machine = state_machine
        
        # Lazy loading de serviços
        self._llm_provider = llm_provider
        self._indexer = indexer
        self._retriever = retriever
        self._prompt_builder = prompt_builder
        self._knowledge_repo = knowledge_repo
        
        # Casos de uso (inicializados sob demanda)
        self._submit_query_use_case: SubmitLegalQueryUseCase | None = None
        self._confirm_piece_use_case: ConfirmPieceUseCase | None = None
        self._collect_data_use_case: CollectDataUseCase | None = None
        self._generate_contract_use_case: GenerateContractUseCase | None = None
        self._generate_document_use_case: GenerateDocumentUseCase | None = None
        self._apply_delta_use_case: ApplyDeltaUseCase | None = None
        self._reset_state_use_case: ResetStateUseCase | None = None
    
    # =========================================================================
    # Propriedades de Serviços (Lazy Loading)
    # =========================================================================
    
    @property
    def llm_provider(self) -> OpenRouterProvider:
        if self._llm_provider is None:
            self._llm_provider = OpenRouterProvider()
        return self._llm_provider
    
    @property
    def indexer(self) -> DocumentIndexer:
        if self._indexer is None:
            self._indexer = DocumentIndexer()
        return self._indexer
    
    @property
    def retriever(self) -> SemanticRetriever:
        if self._retriever is None:
            self._retriever = SemanticRetriever(self.indexer)
        return self._retriever
    
    @property
    def prompt_builder(self) -> RAGPromptBuilder:
        if self._prompt_builder is None:
            self._prompt_builder = RAGPromptBuilder()
        return self._prompt_builder
    
    @property
    def knowledge_repo(self) -> KnowledgeRepository:
        if self._knowledge_repo is None:
            loader = KnowledgeLoader()
            self._knowledge_repo = KnowledgeRepository(loader)
        return self._knowledge_repo
    
    # =========================================================================
    # Métodos de Acesso aos Casos de Uso
    # =========================================================================
    
    @property
    def _uc_submit_query(self) -> SubmitLegalQueryUseCase:
        if self._submit_query_use_case is None:
            self._submit_query_use_case = SubmitLegalQueryUseCase(self.state_machine)
        return self._submit_query_use_case
    
    @property
    def _uc_confirm_piece(self) -> ConfirmPieceUseCase:
        if self._confirm_piece_use_case is None:
            self._confirm_piece_use_case = ConfirmPieceUseCase(self.state_machine)
        return self._confirm_piece_use_case
    
    @property
    def _uc_collect_data(self) -> CollectDataUseCase:
        if self._collect_data_use_case is None:
            self._collect_data_use_case = CollectDataUseCase(self.state_machine)
        return self._collect_data_use_case
    
    @property
    def _uc_generate_contract(self) -> GenerateContractUseCase:
        if self._generate_contract_use_case is None:
            self._generate_contract_use_case = GenerateContractUseCase(
                state_machine=self.state_machine,
                llm_provider=self.llm_provider,
                prompt_builder=self.prompt_builder,
            )
        return self._generate_contract_use_case
    
    @property
    def _uc_generate_document(self) -> GenerateDocumentUseCase:
        if self._generate_document_use_case is None:
            self._generate_document_use_case = GenerateDocumentUseCase(
                state_machine=self.state_machine,
                llm_provider=self.llm_provider,
                vector_store=self.retriever,
                knowledge_repo=self.knowledge_repo,
                prompt_builder=self.prompt_builder,
            )
        return self._generate_document_use_case
    
    @property
    def _uc_apply_delta(self) -> ApplyDeltaUseCase:
        if self._apply_delta_use_case is None:
            self._apply_delta_use_case = ApplyDeltaUseCase(
                state_machine=self.state_machine,
                llm_provider=self.llm_provider,
                knowledge_repo=self.knowledge_repo,
                prompt_builder=self.prompt_builder,
            )
        return self._apply_delta_use_case
    
    @property
    def _uc_reset_state(self) -> ResetStateUseCase:
        if self._reset_state_use_case is None:
            self._reset_state_use_case = ResetStateUseCase(self.state_machine)
        return self._reset_state_use_case
    
    # =========================================================================
    # Métodos Facade (Interface Simplificada para UI)
    # =========================================================================
    
    def submit_legal_query(self, descricao: str, modo: str = "integrado") -> TriagemResponse:
        """
        Submete consulta jurídica (Triagem).
        
        Args:
            descricao: Descrição do caso
            modo: Modo de operação
        
        Returns:
            Resposta da triagem
        """
        request = SubmitLegalQueryRequest(descricao_caso=descricao, modo=modo)
        return self._uc_submit_query.execute(request)
    
    def confirm_piece(
        self,
        dominio: str,
        dominio_nome: str,
        codigo_peca: str,
        codigo_nome: str,
        modo: str,
    ) -> ConfirmacaoResponse:
        """
        Confirma peça jurídica.
        
        Args:
            dominio: ID do domínio
            dominio_nome: Nome do domínio
            codigo_peca: Código da peça
            codigo_nome: Nome da peça
            modo: Modo de operação
        
        Returns:
            Resposta da confirmação
        """
        request = ConfirmPieceRequest(
            dominio=dominio,
            dominio_nome=dominio_nome,
            codigo_peca=codigo_peca,
            codigo_nome=codigo_nome,
            modo=modo,
        )
        return self._uc_confirm_piece.execute(request)
    
    def collect_data(self, dados: dict[str, Any]) -> bool:
        """
        Coleta dados do caso.
        
        Args:
            dados: Dicionário com dados coletados
        
        Returns:
            True se sucesso
        """
        request = CollectDataRequest(dados_coletados=dados)
        return self._uc_collect_data.execute(request)
    
    def generate_contract(self) -> ContratoResponse:
        """
        Gera contrato/briefing.
        
        Returns:
            Resposta com contrato gerado
        """
        return self._uc_generate_contract.execute()
    
    def generate_document_stream(self) -> Generator[str, None, None]:
        """
        Gera documento jurídico com streaming.
        
        Yields:
            Chunks de texto do documento
        """
        yield from self._uc_generate_document.execute()
    
    def apply_delta_stream(
        self,
        peca_atual: str,
        instrucao: str,
        contrato: dict[str, Any],
    ) -> Generator[str, None, None]:
        """
        Aplica modificações na peça com streaming.
        
        Args:
            peca_atual: Texto atual da peça
            instrucao: Instrução de modificação
            contrato: Contrato/briefing
        
        Yields:
            Chunks de texto da peça modificada
        """
        request = ApplyDeltaRequest(
            peca_atual=peca_atual,
            instrucao_delta=instrucao,
            contrato=contrato,
        )
        yield from self._uc_apply_delta.execute(request)
    
    def reset_state(self, session_id: str = "default") -> bool:
        """
        Reinicia todo o estado.
        
        Args:
            session_id: ID da sessão (para futura implementação multi-sessão)
        
        Returns:
            True se sucesso
        """
        return self._uc_reset_state.execute()
    
    def get_session_status(self, session_id: str = "default") -> dict:
        """
        Obtém status da sessão.
        
        Args:
            session_id: ID da sessão
        
        Returns:
            Dicionário com status da sessão
        """
        state = self.get_current_state()
        return {
            "session_id": session_id,
            "etapa": state.etapa,
            "dominio": state.dominio,
            "tem_dados": bool(state.dados_coletados),
            "tem_peca": bool(state.peca_gerada),
        }
    
    def get_current_state(self) -> AppStateDTO:
        """
        Obtém estado atual como DTO.
        
        Returns:
            DTO com estado da aplicação
        """
        state_dict = self.state_machine.to_dict()
        state_dict["etapa_label"] = self.state_machine.etapa_label
        return AppStateDTO.from_state_dict(state_dict)
    
    def get_available_codes(self) -> list[tuple[str, str]]:
        """Obtém códigos disponíveis para o domínio atual."""
        return self._uc_confirm_piece.get_available_codes()
    
    def get_required_fields(self) -> list[dict]:
        """Obtém campos obrigatórios para o código atual."""
        return self._uc_confirm_piece.get_required_fields()
    
    def reiniciar_index(self) -> None:
        """Reinicia o índice RAG."""
        self.indexer.reset()


def create_app_context(state_machine: StateMachine | None = None) -> AppFacade:
    """
    Cria contexto da aplicação com dependências injetadas.
    
    Factory function para criar AppFacade com configuração padrão.
    
    Args:
        state_machine: Instância opcional da StateMachine
    
    Returns:
        Instância de AppFacade pronta para uso
    """
    if state_machine is None:
        state_machine = StateMachine()
    
    return AppFacade(state_machine=state_machine)
