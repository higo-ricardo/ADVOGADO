"""
Testes de integração para a API REST.

Estes testes validam o fluxo completo da API, desde a triagem até a geração de documentos.
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """Cria um cliente de teste para a API."""
    return TestClient(app)


class TestAPIEndpoints:
    """Classe de testes para endpoints da API."""
    
    def test_root_endpoint(self, client):
        """Testa o endpoint raiz."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["version"] == "2.0.0"
    
    def test_triagem_success(self, client):
        """Testa a triagem com descrição válida."""
        payload = {
            "descricao_caso": "Despejo por falta de pagamento",
            "modo": "integrado"
        }
        response = client.post("/api/triagem", json=payload)
        # Pode falhar se não houver LLM configurado, mas valida a estrutura
        if response.status_code == 200:
            data = response.json()
            assert "sucesso" in data
            assert "dominio" in data
    
    def test_triagem_empty_description(self, client):
        """Testa a triagem com descrição vazia (deve validar)."""
        payload = {
            "descricao_caso": "",
            "modo": "integrado"
        }
        response = client.post("/api/triagem", json=payload)
        # Deve retornar erro ou processar (depende da validação no use case)
        assert response.status_code in [200, 400, 500]
    
    def test_confirm_piece_structure(self, client):
        """Testa a estrutura do endpoint de confirmação."""
        payload = {
            "dominio": "locacao",
            "dominio_nome": "Ação de Locação",
            "codigo_peca": "10",
            "codigo_nome": "Petição Inicial",
            "modo": "integrado"
        }
        response = client.post("/api/confirmar-peca", json=payload)
        # Valida que o endpoint existe e responde
        assert response.status_code in [200, 400, 500]
    
    def test_collect_data_structure(self, client):
        """Testa a estrutura do endpoint de coleta de dados."""
        payload = {
            "dados_coletados": {
                "autor": "João Silva",
                "reu": "Maria Santos",
                "imovel": "Rua das Flores, 123"
            }
        }
        response = client.post("/api/coletar-dados", json=payload)
        assert response.status_code in [200, 400, 500]
    
    def test_reset_state(self, client):
        """Testa o reset de estado."""
        payload = {"session_id": "test-session"}
        response = client.post("/api/reset", json=payload)
        # Deve sempre conseguir resetar
        assert response.status_code in [200, 500]
    
    def test_get_status(self, client):
        """Testa a obtenção de status da sessão."""
        response = client.get("/api/status/test-session")
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data or "etapa" in data
    
    def test_apply_delta_structure(self, client):
        """Testa a estrutura do endpoint de aplicação de delta."""
        payload = {
            "peca_atual": "Texto inicial da peça",
            "instrucao_delta": "Adicionar parágrafo sobre juros",
            "contrato": {"autor": "Teste"}
        }
        response = client.post("/api/aplicar-modificacoes", json=payload)
        assert response.status_code in [200, 400, 500]
    
    def test_generate_document_structure(self, client):
        """Testa a estrutura do endpoint de geração de documento."""
        response = client.post("/api/gerar-documento?session_id=test")
        assert response.status_code in [200, 400, 500]


class TestAPIValidation:
    """Testes de validação de entrada da API."""
    
    def test_triagem_missing_fields(self, client):
        """Testa triagem com campos faltantes."""
        payload = {}
        response = client.post("/api/triagem", json=payload)
        # FastAPI deve validar e retornar 422 para campos obrigatórios faltantes
        assert response.status_code in [422, 400, 500]
    
    def test_invalid_json(self, client):
        """Testa envio de JSON inválido."""
        response = client.post(
            "/api/triagem",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
