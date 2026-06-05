"""
tests/core/test_state_machine.py — Testes para o módulo state_machine.

Testa a máquina de estados do agente jurídico de forma isolada,
sem dependências do Streamlit.
"""
import pytest
from core.state_machine import AgentState, Etapa, StateMachine, ETAPA_LABEL


class TestEtapa:
    """Testes para o enum Etapa."""
    
    def test_etapas_existentes(self):
        """Verifica se todas as etapas estão definidas."""
        etapas_esperadas = [
            "triagem",
            "confirmacao",
            "coleta",
            "contrato",
            "geracao",
            "revisao",
        ]
        
        for etapa_valor in etapas_esperadas:
            assert Etapa(etapa_valor) is not None
    
    def test_etapa_labels(self):
        """Verifica se todas as etapas têm labels."""
        for etapa in Etapa:
            assert etapa in ETAPA_LABEL
            assert len(ETAPA_LABEL[etapa]) > 0


class TestAgentState:
    """Testes para a classe AgentState."""
    
    def test_estado_inicial(self):
        """Verifica valores padrão do estado inicial."""
        state = AgentState()
        
        assert state.etapa == Etapa.TRIAGEM
        assert state.descricao_caso == ""
        assert state.dominio is None
        assert state.codigo_peca is None
        assert state.dados_coletados == {}
        assert state.contrato == {}
        assert state.peca_gerada == ""
        assert state.checklist == []
        assert state.erro is None
    
    def test_avancar_etapa(self):
        """Testa avanço de etapa."""
        state = AgentState()
        assert state.etapa == Etapa.TRIAGEM
        
        state.avancar(Etapa.CONFIRMACAO)
        assert state.etapa == Etapa.CONFIRMACAO
        assert state.erro is None  # Erro deve ser limpo ao avançar
    
    def test_reiniciar_estado(self):
        """Testa reinício completo do estado."""
        state = AgentState()
        state.avancar(Etapa.CONFIRMACAO)
        state.descricao_caso = "Caso teste"
        state.dominio = "A"
        
        state.reiniciar()
        
        assert state.etapa == Etapa.TRIAGEM
        assert state.descricao_caso == ""
        assert state.dominio is None
    
    def test_etapa_idx(self):
        """Testa obtenção do índice numérico da etapa."""
        state = AgentState()
        
        assert state.etapa_idx() == 0  # TRIAGEM
        state.avancar(Etapa.CONFIRMACAO)
        assert state.etapa_idx() == 1
        state.avancar(Etapa.COLETA)
        assert state.etapa_idx() == 2
    
    def test_serializacao(self):
        """Testa serialização para dicionário."""
        state = AgentState()
        state.avancar(Etapa.COLETA)
        state.descricao_caso = "Caso teste"
        state.dominio = "A"
        state.codigo_peca = "RPO"
        
        data = state.to_dict()
        
        assert isinstance(data, dict)
        assert data["etapa"] == "coleta"
        assert data["descricao_caso"] == "Caso teste"
        assert data["dominio"] == "A"
        assert data["codigo_peca"] == "RPO"
    
    def test_desserializacao(self):
        """Testa desserialização a partir de dicionário."""
        data = {
            "etapa": "confirmacao",
            "descricao_caso": "Caso teste",
            "dominio": "B",
            "dominio_nome": "Consumerista",
            "codigo_peca": "NEG",
            "codigo_nome": "Negativação indevida",
            "modo": "autonomo",
            "dados_coletados": {"autor": "João"},
            "contrato": {},
            "peca_gerada": "",
            "checklist": [],
            "historico_advogado": [],
            "historico_estagiario": [],
            "erro": None,
        }
        
        state = AgentState.from_dict(data)
        
        assert state.etapa == Etapa.CONFIRMACAO
        assert state.descricao_caso == "Caso teste"
        assert state.dominio == "B"
        assert state.codigo_peca == "NEG"
    
    def test_serializacao_redonda(self):
        """Testa serialização + desserialização (round-trip)."""
        state_original = AgentState()
        state_original.avancar(Etapa.CONTRATO)
        state_original.descricao_caso = "Caso completo"
        state_original.dominio = "F"
        state_original.codigo_peca = "ALI"
        state_original.dados_coletados = {"alimentando": "Pedro"}
        
        # Serializa
        data = state_original.to_dict()
        
        # Desserializa
        state_novo = AgentState.from_dict(data)
        
        # Verifica igualdade
        assert state_novo.etapa == state_original.etapa
        assert state_novo.descricao_caso == state_original.descricao_caso
        assert state_novo.dominio == state_original.dominio
        assert state_novo.codigo_peca == state_original.codigo_peca
        assert state_novo.dados_coletados == state_original.dados_coletados


class TestStateMachine:
    """Testes para a classe StateMachine."""
    
    def test_inicializacao(self):
        """Testa inicialização da state machine."""
        sm = StateMachine()
        assert sm.etapa_atual == Etapa.TRIAGEM
        assert sm.etapa_label == ETAPA_LABEL[Etapa.TRIAGEM]
    
    def test_inicializacao_com_estado(self):
        """Testa inicialização com estado existente."""
        state = AgentState()
        state.avancar(Etapa.GERACAO)
        
        sm = StateMachine(state)
        assert sm.etapa_atual == Etapa.GERACAO
    
    def test_avancar(self):
        """Testa método avançar."""
        sm = StateMachine()
        sm.avancar(Etapa.CONFIRMACAO)
        assert sm.etapa_atual == Etapa.CONFIRMACAO
    
    def test_validar_transicao_permitida(self):
        """Testa validação de transições permitidas."""
        sm = StateMachine()
        
        # Avançar uma etapa é permitido
        assert sm.validar_transicao(Etapa.TRIAGEM, Etapa.CONFIRMACAO) is True
        assert sm.validar_transicao(Etapa.CONFIRMACAO, Etapa.COLETA) is True
        
        # Voltar uma etapa é permitido
        assert sm.validar_transicao(Etapa.CONFIRMACAO, Etapa.TRIAGEM) is True
    
    def test_validar_transicao_proibida(self):
        """Testa validação de transições proibidas."""
        sm = StateMachine()
        
        # Pular etapas não é permitido
        assert sm.validar_transicao(Etapa.TRIAGEM, Etapa.COLETA) is False
        assert sm.validar_transicao(Etapa.TRIAGEM, Etapa.CONTRATO) is False
    
    def test_validar_transicao_reinicio(self):
        """Testa que reinício sempre é permitido."""
        sm = StateMachine()
        
        # Sempre pode voltar para TRIAGEM
        assert sm.validar_transicao(Etapa.COLETA, Etapa.TRIAGEM) is True
        assert sm.validar_transicao(Etapa.GERACAO, Etapa.TRIAGEM) is True
        assert sm.validar_transicao(Etapa.REVISAO, Etapa.TRIAGEM) is True
    
    def test_get_set(self):
        """Testa métodos get e set."""
        sm = StateMachine()
        
        # Get com default
        assert sm.get("descricao_caso") == ""
        assert sm.get("campo_inexistente", "default") == "default"
        
        # Set
        sm.set("descricao_caso", "Novo caso")
        assert sm.get("descricao_caso") == "Novo caso"
        
        # Set em campo inexistente deve falhar
        with pytest.raises(AttributeError):
            sm.set("campo_inexistente", "valor")
    
    def test_to_dict_from_dict(self):
        """Testa serialização completa da state machine."""
        sm = StateMachine()
        sm.avancar(Etapa.COLETA)
        sm.set("descricao_caso", "Caso teste")
        sm.set("dominio", "A")
        
        # Serializa
        data = sm.to_dict()
        
        # Cria nova SM e carrega dados
        sm2 = StateMachine()
        sm2.from_dict(data)
        
        assert sm2.etapa_atual == Etapa.COLETA
        assert sm2.get("descricao_caso") == "Caso teste"
        assert sm2.get("dominio") == "A"
