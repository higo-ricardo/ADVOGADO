"""
src/application/use_cases.py — Casos de Uso da Aplicação.

Cada caso de uso representa uma ação específica que o usuário pode realizar,
orquestrando os serviços necessários para completar a ação.
"""
from __future__ import annotations

import json
from typing import Any, Generator

from core.state_machine import AgentState, Etapa, StateMachine
from core.router import detectar_dominio, codigos_do_dominio, campos_do_codigo

from src.domain.dtos import (
    SubmitLegalQueryRequest,
    TriagemResponse,
    ConfirmPieceRequest,
    ConfirmacaoResponse,
    CollectDataRequest,
    ContratoResponse,
    GenerateDocumentRequest,
    DocumentGenerationResponse,
    ApplyDeltaRequest,
    DeltaResponse,
)
from src.domain.interfaces import (
    LLMProviderProtocol,
    VectorStoreProtocol,
    KnowledgeRepositoryProtocol,
)


# ============================================================================
# Caso de Uso: Submissão de Consulta (Triagem)
# ============================================================================

class SubmitLegalQueryUseCase:
    """
    Caso de uso para submissão inicial de consulta jurídica.
    
    Responsabilidades:
    - Validar descrição do caso
    - Detectar domínio jurídico
    - Atualizar estado da máquina de estados
    """
    
    def __init__(self, state_machine: StateMachine):
        self.state_machine = state_machine
    
    def execute(self, request: SubmitLegalQueryRequest) -> TriagemResponse:
        """
        Executa a triagem da consulta.
        
        Args:
            request: Requisição com descrição do caso
        
        Returns:
            Resposta da triagem com domínio detectado ou erro
        """
        try:
            # Validação básica
            if not request.descricao_caso or len(request.descricao_caso.strip()) < 10:
                return TriagemResponse(
                    sucesso=False,
                    mensagem="Descreva o caso com mais detalhes (mínimo 10 caracteres).",
                )
            
            # Detecta domínio
            resultado = detectar_dominio(request.descricao_caso)
            
            if resultado is None:
                return TriagemResponse(
                    sucesso=False,
                    mensagem="Não foi possível identificar o domínio jurídico. Tente ser mais específico.",
                )
            
            dominio_id, dominio_nome = resultado
            
            # Atualiza estado
            self.state_machine.set("descricao_caso", request.descricao_caso)
            self.state_machine.set("dominio", dominio_id)
            self.state_machine.set("dominio_nome", dominio_nome)
            self.state_machine.set("modo", request.modo)
            self.state_machine.avancar(Etapa.CONFIRMACAO)
            
            return TriagemResponse(
                sucesso=True,
                dominio=dominio_id,
                dominio_nome=dominio_nome,
                mensagem=f"Domínio identificado: {dominio_nome}",
            )
            
        except Exception as exc:
            return TriagemResponse(
                sucesso=False,
                erro=str(exc),
                mensagem="Erro ao processar consulta.",
            )


# ============================================================================
# Caso de Uso: Confirmação de Peça
# ============================================================================

class ConfirmPieceUseCase:
    """
    Caso de uso para confirmação do tipo de peça jurídica.
    
    Responsabilidades:
    - Listar códigos disponíveis para o domínio
    - Validar seleção do usuário
    - Avançar para coleta de dados
    """
    
    def __init__(self, state_machine: StateMachine):
        self.state_machine = state_machine
    
    def execute(self, request: ConfirmPieceRequest) -> ConfirmacaoResponse:
        """
        Executa a confirmação da peça.
        
        Args:
            request: Requisição com código da peça selecionado
        
        Returns:
            Resposta com códigos disponíveis ou erro
        """
        try:
            dominio = self.state_machine.get("dominio")
            
            if not dominio:
                return ConfirmacaoResponse(
                    sucesso=False,
                    mensagem="Domínio não identificado. Reinicie o processo.",
                )
            
            # Obtém códigos disponíveis
            codigos = codigos_do_dominio(dominio)
            
            # Valida se o código selecionado é válido
            codigo_valido = any(c[0] == request.codigo_peca for c in codigos)
            
            if not codigo_valido:
                return ConfirmacaoResponse(
                    sucesso=False,
                    codigos_disponiveis=codigos,
                    mensagem="Código de peça inválido.",
                )
            
            # Atualiza estado
            self.state_machine.set("codigo_peca", request.codigo_peca)
            self.state_machine.set("codigo_nome", request.codigo_nome)
            self.state_machine.set("modo", request.modo)
            self.state_machine.avancar(Etapa.COLETA)
            
            return ConfirmacaoResponse(
                sucesso=True,
                codigos_disponiveis=codigos,
                mensagem=f"Peça confirmada: {request.codigo_nome}",
            )
            
        except Exception as exc:
            return ConfirmacaoResponse(
                sucesso=False,
                erro=str(exc),
                mensagem="Erro ao confirmar peça.",
            )
    
    def get_available_codes(self) -> list[tuple[str, str]]:
        """Obtém códigos disponíveis para o domínio atual."""
        dominio = self.state_machine.get("dominio")
        if not dominio:
            return []
        return codigos_do_dominio(dominio)
    
    def get_required_fields(self) -> list[dict]:
        """Obtém campos obrigatórios para o código atual."""
        codigo = self.state_machine.get("codigo_peca")
        if not codigo:
            return []
        return campos_do_codigo(codigo)


# ============================================================================
# Caso de Uso: Coleta de Dados
# ============================================================================

class CollectDataUseCase:
    """
    Caso de uso para coleta de dados do caso.
    
    Responsabilidades:
    - Armazenar dados coletados
    - Validar completude dos dados
    - Avançar para geração de contrato
    """
    
    def __init__(self, state_machine: StateMachine):
        self.state_machine = state_machine
    
    def execute(self, request: CollectDataRequest) -> bool:
        """
        Executa a coleta de dados.
        
        Args:
            request: Requisição com dados coletados
        
        Returns:
            True se sucesso, False se falhou
        """
        try:
            # Valida dados obrigatórios
            codigo = self.state_machine.get("codigo_peca")
            campos = campos_do_codigo(codigo) if codigo else []
            
            campos_obrigatorios = [c["id"] for c in campos]
            dados_fornecidos = set(request.dados_coletados.keys())
            
            # Verifica se todos os campos obrigatórios foram preenchidos
            faltantes = set(campos_obrigatorios) - dados_fornecidos
            
            if faltantes:
                raise ValueError(f"Campos obrigatórios faltantes: {', '.join(faltantes)}")
            
            # Armazena dados
            self.state_machine.set("dados_coletados", request.dados_coletados)
            self.state_machine.avancar(Etapa.CONTRATO)
            
            return True
            
        except Exception as exc:
            self.state_machine.set("erro", str(exc))
            return False


# ============================================================================
# Caso de Uso: Geração de Contrato/Briefing
# ============================================================================

class GenerateContractUseCase:
    """
    Caso de uso para geração de contrato/briefing.
    
    Responsabilidades:
    - Montar prompt contextualizado
    - Chamar LLM para gerar contrato estruturado
    - Parsear e validar resposta JSON
    """
    
    def __init__(
        self,
        state_machine: StateMachine,
        llm_provider: LLMProviderProtocol,
        prompt_builder: Any,
    ):
        self.state_machine = state_machine
        self.llm_provider = llm_provider
        self.prompt_builder = prompt_builder
    
    def execute(self) -> ContratoResponse:
        """
        Executa a geração do contrato.
        
        Returns:
            Resposta com contrato gerado ou erro
        """
        try:
            # Coleta dados do estado
            descricao_caso = self.state_machine.get("descricao_caso", "")
            dominio = self.state_machine.get("dominio", "")
            dominio_nome = self.state_machine.get("dominio_nome", "")
            codigo = self.state_machine.get("codigo_peca", "")
            codigo_nome = self.state_machine.get("codigo_nome", "")
            modo = self.state_machine.get("modo", "integrado")
            dados_coletados = self.state_machine.get("dados_coletados", {})
            
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
            
            # Chama LLM
            response = self.llm_provider.chat_completion(
                messages=messages,
                stream=False,
                max_tokens=2048,
                temperature=0.3,
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extrai JSON
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            contrato = json.loads(content)
            
            # Armazena contrato
            self.state_machine.set("contrato", contrato)
            
            return ContratoResponse(
                sucesso=True,
                contrato=contrato,
                mensagem="Contrato gerado com sucesso.",
            )
            
        except json.JSONDecodeError as exc:
            return ContratoResponse(
                sucesso=False,
                erro=f"Falha ao parsear JSON: {exc}",
                mensagem="Erro ao processar resposta do LLM.",
            )
        except Exception as exc:
            return ContratoResponse(
                sucesso=False,
                erro=str(exc),
                mensagem="Erro ao gerar contrato.",
            )


# ============================================================================
# Caso de Uso: Geração de Documento
# ============================================================================

class GenerateDocumentUseCase:
    """
    Caso de uso para geração de documento jurídico com streaming.
    
    Responsabilidades:
    - Preparar contexto RAG
    - Montar prompt com minuta e trechos relevantes
    - Streamar resposta do LLM
    """
    
    def __init__(
        self,
        state_machine: StateMachine,
        llm_provider: LLMProviderProtocol,
        vector_store: VectorStoreProtocol,
        knowledge_repo: KnowledgeRepositoryProtocol,
        prompt_builder: Any,
    ):
        self.state_machine = state_machine
        self.llm_provider = llm_provider
        self.vector_store = vector_store
        self.knowledge_repo = knowledge_repo
        self.prompt_builder = prompt_builder
    
    def execute(self) -> Generator[str, None, None]:
        """
        Executa a geração do documento com streaming.
        
        Yields:
            Chunks de texto do documento sendo gerado
        """
        try:
            # Coleta dados do estado
            contrato = self.state_machine.get("contrato", {})
            codigo = self.state_machine.get("codigo_peca", "")
            
            # Indexa documentos se necessário
            if not self.vector_store.is_indexed:
                self._indexar_documentos(codigo)
            
            # Busca trechos relevantes
            query = f"{contrato.get('escopo', '')} {codigo}"
            trechos = self.vector_store.search(query, top_k=5)
            
            # Monta contexto
            contexto_estagiario = self.knowledge_repo.build_contexto_estagiario(codigo)
            
            # Monta prompt
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
            peca_completa = ""
            for chunk in self.llm_provider.chat_completion_stream(
                messages=messages,
                max_tokens=4096,
                temperature=0.7,
            ):
                peca_completa += chunk
                yield chunk
            
            # Armazena peça gerada
            self.state_machine.set("peca_gerada", peca_completa)
            
            # Gera checklist básico
            checklist = self._gerar_checklist(peca_completa, codigo)
            self.state_machine.set("checklist", checklist)
            
            self.state_machine.avancar(Etapa.REVISAO)
            
        except Exception as exc:
            self.state_machine.set("erro", str(exc))
            yield f"\n\n[ERRO: {exc}]"
    
    def _indexar_documentos(self, codigo: str) -> int:
        """Indexa documentos da base de conhecimento."""
        documentos: dict[str, str] = {}
        
        # Minuta específica
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
        
        return self.vector_store.add_documents(documentos)
    
    def _gerar_checklist(self, peca: str, codigo: str) -> list[str]:
        """Gera checklist básico de revisão."""
        checklist = []
        
        # Verificações básicas
        if "Excelentíssimo" not in peca and "Meritíssimo" not in peca:
            checklist.append("⚠️ Verificar vocativo inicial")
        
        if "Nestes termos," not in peca:
            checklist.append("⚠️ Verificar fechamento")
        
        if "pede deferimento" not in peca.lower():
            checklist.append("⚠️ Verificar fórmula de pedido final")
        
        # Verifica campos específicos por código
        campos = campos_do_codigo(codigo)
        for campo in campos:
            if campo["id"] not in peca:
                checklist.append(f"⚠️ Verificar inclusão de: {campo['label']}")
        
        return checklist if checklist else ["✅ Checklist completo"]


# ============================================================================
# Caso de Uso: Aplicação de Delta (Modificações)
# ============================================================================

class ApplyDeltaUseCase:
    """
    Caso de uso para aplicação de modificações em peça existente.
    
    Responsabilidades:
    - Receber instruções de modificação
    - Aplicar delta usando LLM
    - Streamar resultado modificado
    """
    
    def __init__(
        self,
        state_machine: StateMachine,
        llm_provider: LLMProviderProtocol,
        knowledge_repo: KnowledgeRepositoryProtocol,
        prompt_builder: Any,
    ):
        self.state_machine = state_machine
        self.llm_provider = llm_provider
        self.knowledge_repo = knowledge_repo
        self.prompt_builder = prompt_builder
    
    def execute(self, request: ApplyDeltaRequest) -> Generator[str, None, None]:
        """
        Executa a aplicação de delta.
        
        Args:
            request: Requisição com peça atual e instrução de modificação
        
        Yields:
            Chunks de texto da peça modificada
        """
        try:
            # Monta prompt
            prompt = self.prompt_builder.build_delta_prompt(
                peca_atual=request.peca_atual,
                instrucao_delta=request.instrucao_delta,
                contrato=request.contrato,
            )
            
            system_prompt = self.knowledge_repo.get_system_advogado()
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
            
            # Streaming
            peca_modificada = ""
            for chunk in self.llm_provider.chat_completion_stream(
                messages=messages,
                max_tokens=4096,
                temperature=0.5,
            ):
                peca_modificada += chunk
                yield chunk
            
            # Atualiza peça no estado
            self.state_machine.set("peca_gerada", peca_modificada)
            
        except Exception as exc:
            self.state_machine.set("erro", str(exc))
            yield f"\n\n[ERRO: {exc}]"


# ============================================================================
# Caso de Uso: Reset de Estado
# ============================================================================

class ResetStateUseCase:
    """
    Caso de uso para reiniciar todo o estado da aplicação.
    
    Responsabilidades:
    - Limpar todos os dados do estado
    - Reiniciar para etapa inicial
    """
    
    def __init__(self, state_machine: StateMachine):
        self.state_machine = state_machine
    
    def execute(self) -> bool:
        """
        Executa o reset do estado.
        
        Returns:
            True se sucesso
        """
        try:
            self.state_machine.reiniciar()
            return True
        except Exception:
            return False
