"""
ui/adapters.py — Adaptadores entre UI (Streamlit) e Core.

Este módulo traduz eventos da UI em comandos do Core,
mantendo pages.py limpo e focado apenas em renderização.

Diferente do agent.py original, este módulo:
- Não contém lógica de negócio (apenas orquestra serviços)
- É testável (pode ser mockado em testes)
- Usa os serviços modularizados (LLM, RAG, Knowledge)
"""
from __future__ import annotations

import json
from typing import Any, Generator

from infrastructure.config import config
from infrastructure.exceptions import AgentError, LLMError, RAGError
from services.llm.openrouter import OpenRouterProvider
from services.rag.indexer import DocumentIndexer
from services.rag.retriever import SemanticRetriever
from services.rag.prompt_builder import RAGPromptBuilder
from services.knowledge.loader import KnowledgeLoader
from services.knowledge.repository import KnowledgeRepository


class UIAdapter:
    """
    Adaptador entre UI e serviços do Core.
    
    Responsabilidades:
    - Orquestrar chamadas aos serviços
    - Traduzir dados entre formatos UI ↔ Core
    - Fornecer interface simplificada para pages.py
    """
    
    def __init__(self):
        """Inicializa o adapter com todos os serviços necessários."""
        self._llm: OpenRouterProvider | None = None
        self._indexer: DocumentIndexer | None = None
        self._retriever: SemanticRetriever | None = None
        self._prompt_builder: RAGPromptBuilder | None = None
        self._knowledge_repo: KnowledgeRepository | None = None
    
    @property
    def llm(self) -> OpenRouterProvider:
        """Lazy loading do provedor LLM."""
        if self._llm is None:
            self._llm = OpenRouterProvider()
        return self._llm
    
    @property
    def indexer(self) -> DocumentIndexer:
        """Lazy loading do indexador RAG."""
        if self._indexer is None:
            self._indexer = DocumentIndexer()
        return self._indexer
    
    @property
    def retriever(self) -> SemanticRetriever:
        """Lazy loading do recuperador semântico."""
        if self._retriever is None:
            self._retriever = SemanticRetriever(self.indexer)
        return self._retriever
    
    @property
    def prompt_builder(self) -> RAGPromptBuilder:
        """Lazy loading do construtor de prompts."""
        if self._prompt_builder is None:
            self._prompt_builder = RAGPromptBuilder()
        return self._prompt_builder
    
    @property
    def knowledge_repo(self) -> KnowledgeRepository:
        """Lazy loading do repositório de conhecimento."""
        if self._knowledge_repo is None:
            loader = KnowledgeLoader()
            self._knowledge_repo = KnowledgeRepository(loader)
        return self._knowledge_repo
    
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
        Gera contrato/briefing do caso.
        
        Args:
            descricao_caso: Descrição do caso
            dominio: ID do domínio
            dominio_nome: Nome do domínio
            codigo: Código da peça
            codigo_nome: Nome da peça
            modo: Modo de operação
            dados_coletados: Dados coletados
        
        Returns:
            Dicionário com contrato/briefing
        
        Raises:
            AgentError: Se falhar na geração
        """
        # Monta prompt
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
            
            # Tenta extrair JSON da resposta
            # Às vezes o modelo inclui markdown ```json ... ```
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            contrato = json.loads(content)
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
        Gera peça jurídica com streaming (papel do estagiário).
        
        Args:
            contrato: Contrato/briefing do caso
            codigo: Código da peça
        
        Yields:
            Chunks de texto da peça sendo gerada
        
        Raises:
            AgentError: Se falhar na geração
        """
        try:
            # Indexa documentos se necessário
            if not self.indexer.is_indexed:
                self._indexar_documentos(codigo)
            
            # Busca trechos relevantes
            query = f"{contrato.get('escopo', '')} {codigo}"
            trechos = self.retriever.search(query, top_k=config.RAG_TOP_K)
            
            # Monta contexto completo
            contexto_estagiario = self.knowledge_repo.build_contexto_estagiario(codigo)
            
            # Monta prompt final
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
            
            # Streaming
            for chunk in self.llm.chat_completion_stream(
                messages=messages,
                max_tokens=config.MAX_TOKENS,
                temperature=0.7,
            ):
                yield chunk
                
        except Exception as exc:
            raise AgentError(f"Erro na redação da peça: {exc}")
    
    def advogado_delta(
        self,
        peca_atual: str,
        instrucao_delta: str,
        contrato: dict[str, Any],
    ) -> Generator[str, None, None]:
        """
        Aplica modificações (delta) em uma peça existente.
        
        Args:
            peca_atual: Texto atual da peça
            instrucao_delta: Instrução de modificação
            contrato: Contrato/briefing
        
        Yields:
            Chunks de texto da peça modificada
        
        Raises:
            AgentError: Se falhar na aplicação do delta
        """
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
                yield chunk
                
        except Exception as exc:
            raise AgentError(f"Erro ao aplicar delta: {exc}")
    
    def _indexar_documentos(self, codigo: str) -> int:
        """
        Indexa documentos da base de conhecimento.
        
        Args:
            codigo: Código da peça (para carregar minuta específica)
        
        Returns:
            Número de chunks indexados
        """
        # Carrega todos os documentos relevantes
        documentos: dict[str, str] = {}
        
        # Minuta específica do código
        try:
            minuta = self.knowledge_repo.get_minuta_por_codigo(codigo)
            documentos[f"minuta_{codigo}"] = minuta
        except Exception:
            pass
        
        # Estilo e formatação
        try:
            documentos["estilo"] = self.knowledge_repo.get_estilo()
            documentos["formatacao"] = self.knowledge_repo.get_minuta_base()
        except Exception:
            pass
        
        # Fontes normativas
        try:
            documentos["fontes"] = self.knowledge_repo.get_fontes()
        except Exception:
            pass
        
        # Indexa
        return self.indexer.index_documents(documentos)
    
    def reiniciar_index(self) -> None:
        """Reinicia o índice RAG (útil para recarregar documentos)."""
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


# Compatibilidade com imports diretos
__all__ = ["UIAdapter", "get_adapter"]


# ============================================================================
# State Machine Adapters (para integração com Streamlit)
# ============================================================================

def get_state_machine() -> Any:
    """
    Obtém ou cria instância da State Machine no session_state.
    
    Returns:
        StateMachine instância
    """
    import streamlit as st
    
    if "state_machine" not in st.session_state:
        from core.state_machine import StateMachine
        st.session_state.state_machine = StateMachine()
    
    return st.session_state.state_machine


def save_state_machine(state_machine: Any) -> None:
    """
    Salva a State Machine no session_state.
    
    Args:
        state_machine: Instância da StateMachine
    """
    import streamlit as st
    st.session_state.state_machine = state_machine
