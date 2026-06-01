"""
state.py — State machine centralizado do agente jurídico.
Gerencia as 6 etapas do fluxo e todos os dados de sessão.
"""
import streamlit as st
from enum import Enum


class Etapa(str, Enum):
    TRIAGEM = "triagem"           # 1. Usuário descreve o caso
    CONFIRMACAO = "confirmacao"   # 2. Confirmar domínio + código da peça
    COLETA = "coleta"             # 3. Preencher dados faltantes
    CONTRATO = "contrato"         # 4. Revisar contrato gerado
    GERACAO = "geracao"           # 5. Geração da peça (streaming)
    REVISAO = "revisao"           # 6. Checklist + aprovação + download


ETAPA_LABEL = {
    Etapa.TRIAGEM:     "1. Descrever o caso",
    Etapa.CONFIRMACAO: "2. Confirmar peça",
    Etapa.COLETA:      "3. Dados do caso",
    Etapa.CONTRATO:    "4. Revisar briefing",
    Etapa.GERACAO:     "5. Gerando peça",
    Etapa.REVISAO:     "6. Revisão e download",
}

DEFAULTS: dict = {
    "etapa": Etapa.TRIAGEM,
    "descricao_caso": "",
    "dominio": None,          # "A", "B", "C", etc.
    "dominio_nome": None,     # "Consumerista / JEC"
    "codigo_peca": None,      # "NEG", "ATR", etc.
    "codigo_nome": None,      # "Negativação indevida"
    "modo": None,             # "autonomo" | "integrado"
    "dados_coletados": {},    # campos obrigatórios preenchidos
    "contrato": {},           # contrato_decisao serializado
    "peca_gerada": "",        # texto da peça final
    "checklist": [],          # itens de aderência
    "historico_advogado": [], # mensagens para o orquestrador
    "historico_estagiario":[], # mensagens para o executor
    "erro": None,
}


def init():
    """Inicializa todos os estados com valores padrão."""
    for chave, valor in DEFAULTS.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def get(chave, default=None):
    return st.session_state.get(chave, default)


def set(chave, valor):
    st.session_state[chave] = valor


def avancar(proxima: Etapa):
    st.session_state["etapa"] = proxima
    st.session_state["erro"] = None


def reiniciar():
    """Limpa tudo e volta para triagem."""
    for chave, valor in DEFAULTS.items():
        st.session_state[chave] = valor


def etapa_atual() -> Etapa:
    return st.session_state.get("etapa", Etapa.TRIAGEM)


def etapa_idx() -> int:
    return list(Etapa).index(etapa_atual())
