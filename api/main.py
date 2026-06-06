"""
API REST para o Agente Jurídico IA.

Esta API expõe a lógica de negócio (AppFacade) via endpoints REST,
permitindo integração com frontends externos (React, Mobile, etc).
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any, Optional

# Importação da camada de aplicação e DTOs
from src.application.app_facade import AppFacade, create_app_context
from src.domain.dtos import (
    SubmitLegalQueryRequest,
    ConfirmPieceRequest,
    CollectDataRequest,
    ApplyDeltaRequest,
    ResetStateRequest,
    TriagemResponse,
    ConfirmacaoResponse,
    ContratoResponse,
    ErrorDTO
)

# Configuração de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação, inicializando o contexto."""
    logger.info("Inicializando contexto da aplicação...")
    app.state.app_context = create_app_context()
    logger.info("Contexto inicializado com sucesso.")
    yield
    logger.info("Encerrando aplicação...")


app = FastAPI(
    title="Agente Jurídico IA API",
    description="API para geração e análise de peças jurídicas assistida por IA.",
    version="2.0.0",
    lifespan=lifespan
)

# Configuração de CORS (permite requisições de qualquer origem em dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_app_context() -> AppFacade:
    """Recupera o contexto da aplicação do estado do FastAPI."""
    return app.state.app_context


@app.get("/")
async def root():
    """Endpoint de saúde e informações básicas."""
    return {
        "status": "online",
        "service": "Agente Jurídico IA",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.post("/api/triagem", response_model=TriagemResponse)
async def submit_triagem(request: SubmitLegalQueryRequest):
    """
    Inicia o processo de triagem de uma demanda jurídica.
    
    Recebe a descrição do caso e retorna o domínio detectado e as peças sugeridas.
    """
    try:
        context = get_app_context()
        result = context.submit_legal_query(request.descricao_caso, request.modo)
        return result
    except Exception as e:
        logger.error(f"Erro na triagem: {str(e)}")
        raise HTTPException(status_code=500, detail={"codigo": "TRIAGEM_ERROR", "mensagem": str(e)})


@app.post("/api/confirmar-peca", response_model=ConfirmacaoResponse)
async def confirm_piece(request: ConfirmPieceRequest):
    """
    Confirma a peça jurídica selecionada pelo usuário.
    
    Valida a seleção e prepara o estado para a coleta de dados.
    """
    try:
        context = get_app_context()
        result = context.confirm_piece(
            dominio=request.dominio,
            dominio_nome=request.dominio_nome,
            codigo_peca=request.codigo_peca,
            codigo_nome=request.codigo_nome,
            modo=request.modo,
        )
        return result
    except Exception as e:
        logger.error(f"Erro na confirmação: {str(e)}")
        raise HTTPException(status_code=500, detail={"codigo": "CONFIRMACAO_ERROR", "mensagem": str(e)})


@app.post("/api/coletar-dados", response_model=ContratoResponse)
async def collect_data(request: CollectDataRequest):
    """
    Coleta os dados necessários para a geração do documento.
    
    Recebe os dados estruturados e avança para a etapa de geração.
    """
    try:
        context = get_app_context()
        result = context.collect_data(request.dados_coletados)
        return ContratoResponse(sucesso=result, contrato=context.get_current_state().contrato)
    except Exception as e:
        logger.error(f"Erro na coleta de dados: {str(e)}")
        raise HTTPException(status_code=500, detail={"codigo": "COLETA_ERROR", "mensagem": str(e)})


@app.post("/api/gerar-documento")
async def generate_document(background_tasks: BackgroundTasks, session_id: str = "default"):
    """
    Gera o documento jurídico completo.
    
    Esta operação pode ser demorada, então é executada em background se necessário,
    mas retorna o resultado final para simplificação nesta versão.
    """
    try:
        context = get_app_context()
        # Nota: A implementação atual do use_case pode precisar de adaptação para assincronia
        # ou uso de tasks em background reais dependendo do tempo de resposta do LLM.
        chunks = list(context.generate_document_stream())
        peca_gerada = "".join(chunks)
        state = context.get_current_state()
        return {
            "sucesso": True,
            "peca_gerada": peca_gerada,
            "checklist": state.checklist,
        }
    except Exception as e:
        logger.error(f"Erro na geração: {str(e)}")
        return {"sucesso": False, "erro": str(e)}


@app.post("/api/aplicar-modificacoes")
async def apply_delta(request: ApplyDeltaRequest):
    """
    Aplica modificações (deltas) ao documento gerado.
    
    Permite que o usuário refine o texto através de comandos naturais.
    """
    try:
        context = get_app_context()
        # Coleta chunks e junta para resposta síncrona
        chunks = list(context.apply_delta_stream(
            peca_atual=request.peca_atual,
            instrucao=request.instrucao_delta,
            contrato=request.contrato,
        ))
        peca_modificada = "".join(chunks)
        return {"sucesso": True, "peca_modificada": peca_modificada}
    except Exception as e:
        logger.error(f"Erro ao aplicar modificações: {str(e)}")
        raise HTTPException(status_code=500, detail={"codigo": "DELTA_ERROR", "mensagem": str(e)})


@app.post("/api/reset")
async def reset_state(request: ResetStateRequest):
    """
    Reseta o estado da sessão para a etapa inicial (triagem).
    """
    try:
        context = get_app_context()
        context.reset_state(request.session_id)
        return {"status": "success", "message": "Estado resetado com sucesso."}
    except Exception as e:
        logger.error(f"Erro ao resetar estado: {str(e)}")
        raise HTTPException(status_code=500, detail={"codigo": "INTERNAL_ERROR", "mensagem": str(e)})


@app.get("/api/status/{session_id}")
async def get_status(session_id: str):
    """
    Retorna o estado atual de uma sessão específica.
    Útil para verificar o progresso de operações longas ou recuperar estado.
    """
    try:
        context = get_app_context()
        status = context.get_session_status(session_id)
        return status
    except Exception as e:
        logger.error(f"Erro ao buscar status: {str(e)}")
        # Retorna status básico mesmo com erro
        return {"session_id": session_id, "etapa": "desconhecido", "erro": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
