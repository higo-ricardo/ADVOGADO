"""
Testes para o módulo Router.
"""
import pytest
from core import router


class TestRouter:
    """Testes unitários para o módulo router."""

    def test_router_config_initialization(self, sample_router_config):
        """Testa inicialização da configuração do router."""
        config = router.RouterConfig(config_path=str(sample_router_config))
        assert config.keywords is not None
        assert config.codigos_por_dominio is not None

    def test_detectar_dominio_esbulho(self, sample_router_config):
        """Testa identificação de domínio para caso de esbulho."""
        # Recarrega config com arquivo de teste
        router._config = router.RouterConfig(config_path=str(sample_router_config))
        descricao = "Meu cliente sofreu esbulho de sua propriedade rural há 3 meses."
        
        resultado = router.detectar_dominio(descricao)
        
        assert resultado is not None
        assert resultado[0] == "A"
        assert resultado[1] == "Imobiliário"

    def test_detectar_dominio_negativacao(self, sample_router_config):
        """Testa identificação de domínio para negativação indevida."""
        router._config = router.RouterConfig(config_path=str(sample_router_config))
        descricao = "Houve negativação indevida do nome do autor no SPC."
        
        resultado = router.detectar_dominio(descricao)
        
        assert resultado is not None
        assert resultado[0] == "B"
        assert resultado[1] == "Consumerista / JEC"

    def test_detectar_dominio_sem_match(self, sample_router_config):
        """Testa caso sem match de domínio (deve retornar None)."""
        router._config = router.RouterConfig(config_path=str(sample_router_config))
        descricao = "Questão sobre direito internacional não mapeado."
        
        resultado = router.detectar_dominio(descricao)
        
        assert resultado is None

    def test_codigos_do_dominio(self, sample_router_config):
        """Testa listagem de códigos por domínio."""
        router._config = router.RouterConfig(config_path=str(sample_router_config))
        
        codigos = router.codigos_do_dominio("A")
        
        assert len(codigos) > 0
        assert any("RPO" in str(c) for c in codigos)
        assert any("MPO" in str(c) for c in codigos)

    def test_is_autonomo(self, sample_router_config):
        """Testa verificação de código autônomo."""
        router._config = router.RouterConfig(config_path=str(sample_router_config))
        
        assert router.is_autonomo("CHO") is True
        assert router.is_autonomo("PRO") is True
        assert router.is_autonomo("DHI") is True
        assert router.is_autonomo("RPO") is False

    def test_campos_do_codigo_rpo(self):
        """Testa obtenção de campos para código RPO."""
        campos = router.campos_do_codigo("RPO")
        
        assert len(campos) > 0
        assert any(c["id"] == "autor" for c in campos)
        assert any(c["id"] == "reu" for c in campos)
        assert any(c["id"] == "imovel" for c in campos)

    def test_campos_do_codigo_inexistente(self):
        """Testa campos para código que não existe."""
        campos = router.campos_do_codigo("XXX")
        
        # Deve retornar lista vazia ou campos padrão
        assert isinstance(campos, list)

    def test_detectar_dominio_case_insensitive(self, sample_router_config):
        """Testa se identificação é case insensitive."""
        router._config = router.RouterConfig(config_path=str(sample_router_config))
        
        descricao_lower = "esbulho possessório"
        descricao_upper = "ESBULHO POSSESSÓRIO"
        descricao_mixed = "EsBuLhO pOsSeSsÓrIo"
        
        dom_low = router.detectar_dominio(descricao_lower)
        dom_up = router.detectar_dominio(descricao_upper)
        dom_mix = router.detectar_dominio(descricao_mixed)
        
        assert dom_low == dom_up == dom_mix
