"""
conftest.py — Fixtures e configurações para testes pytest.

Este módulo fornece fixtures reutilizáveis para todos os testes do projeto.
"""
import pytest
from pathlib import Path


# -----------------------------------------------------------------------------
# Fixtures de configuração
# -----------------------------------------------------------------------------

@pytest.fixture
def sample_knowledge_dir(tmp_path: Path) -> Path:
    """Cria um diretório de conhecimento temporário com arquivos de exemplo."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    
    # Cria arquivos de exemplo
    (knowledge_dir / "estilo_juridico.md").write_text(
        "# Estilo Jurídico\n\nUse linguagem formal e técnica...",
        encoding="utf-8"
    )
    (knowledge_dir / "minuta-base.md").write_text(
        "# Minuta Base\n\nFragmentos de formatação...",
        encoding="utf-8"
    )
    (knowledge_dir / "advogado.md").write_text(
        "# System Prompt Advogado\n\nVocê é um advogado experiente...",
        encoding="utf-8"
    )
    (knowledge_dir / "estagiario.md").write_text(
        "# System Prompt Estagiário\n\nVocê é um estagiário de direito...",
        encoding="utf-8"
    )
    
    return knowledge_dir


@pytest.fixture
def sample_router_config(tmp_path: Path) -> Path:
    """Cria um arquivo de configuração de router temporário."""
    config_file = tmp_path / "router_config.yaml"
    config_content = """
dominios:
  keywords:
    esbulho: ["A", "Imobiliário"]
    posse: ["A", "Imobiliário"]
    reintegracao: ["A", "Imobiliário"]
    negativação: ["B", "Consumerista / JEC"]
    spc: ["B", "Consumerista / JEC"]
    serasa: ["B", "Consumerista / JEC"]

codigos_por_dominio:
  A:
    - ["RPO", "Reintegração de posse (esbulho)"]
    - ["MPO", "Manutenção de posse (turbação)"]
  B:
    - ["NEG", "Ação de negativação indevida"]
    - ["PSC", "Cancelamento de plano de saúde"]

codigos_autonomos:
  - CHO
  - PRO
  - DHI
"""
    config_file.write_text(config_content, encoding="utf-8")
    return config_file


# -----------------------------------------------------------------------------
# Fixtures de estado
# -----------------------------------------------------------------------------

@pytest.fixture
def sample_estado_triagem():
    """Retorna um estado de exemplo na etapa de triagem."""
    return {
        "etapa": "triagem",
        "descricao_caso": "Meu cliente foi esbulhado de sua propriedade rural há 3 meses.",
        "dominio": None,
        "dominio_nome": None,
        "codigo_peca": None,
        "codigo_nome": None,
        "modo": None,
        "dados_coletados": {},
        "contrato": {},
        "peca_gerada": "",
        "checklist": [],
        "historico_advogado": [],
        "historico_estagiario": [],
        "erro": None,
    }


@pytest.fixture
def sample_estado_confirmacao():
    """Retorna um estado de exemplo na etapa de confirmação."""
    return {
        "etapa": "confirmacao",
        "descricao_caso": "Meu cliente foi esbulhado de sua propriedade rural há 3 meses.",
        "dominio": "A",
        "dominio_nome": "Imobiliário",
        "codigo_peca": None,
        "codigo_nome": None,
        "modo": None,
        "dados_coletados": {},
        "contrato": {},
        "peca_gerada": "",
        "checklist": [],
        "historico_advogado": [],
        "historico_estagiario": [],
        "erro": None,
    }


@pytest.fixture
def sample_estado_coleta():
    """Retorna um estado de exemplo na etapa de coleta."""
    return {
        "etapa": "coleta",
        "descricao_caso": "Meu cliente foi esbulhado de sua propriedade rural há 3 meses.",
        "dominio": "A",
        "dominio_nome": "Imobiliário",
        "codigo_peca": "RPO",
        "codigo_nome": "Reintegração de posse (esbulho)",
        "modo": "autonomo",
        "dados_coletados": {
            "autor": "João da Silva",
            "reu": "Maria dos Santos",
            "imovel": "Terreno rural de 50 hectares",
            "data_esbulho": "15/03/2024",
            "forca": "Nova (menos de 1 ano e 1 dia)",
        },
        "contrato": {},
        "peca_gerada": "",
        "checklist": [],
        "historico_advogado": [],
        "historico_estagiario": [],
        "erro": None,
    }


@pytest.fixture
def sample_contrato():
    """Retorna um contrato/briefing de exemplo."""
    return {
        "escopo": "Reintegração de posse por esbulho recente",
        "tipo_peca": "RPO — Reintegração de posse (esbulho)",
        "dominio": "A — Imobiliário",
        "modo": "autonomo",
        "pedidos": [
            "Reintegração de posse do imóvel",
            "Indenização por danos materiais",
            "Condenação em honorários advocatícios",
        ],
        "criterios_aceite": [
            "Comprovar posse anterior do autor",
            "Demonstrar esbulho recente (menos de 1 ano)",
            "Pedir liminar inaudita altera parte",
        ],
        "regras_criticas": [
            "Verificar prazo decadencial de 1 ano e 1 dia",
            "Incluir pedido de liminar fundamentado no art. 562 do CPC",
        ],
        "dados": {
            "autor": "João da Silva",
            "reu": "Maria dos Santos",
        },
        "dependencias": ["fontes.md", "verbetesSTJ.md"],
        "observacoes": "Caso simples de esbulho recente",
    }


# -----------------------------------------------------------------------------
# Fixtures de documentos
# -----------------------------------------------------------------------------

@pytest.fixture
def sample_documentos_rag():
    """Retorna documentos de exemplo para teste de RAG."""
    return {
        "minuta_rpo": """
# Ação de Reintegração de Posse

## Fundamentação
O esbulho possessório ocorre quando há perda da posse...

## Pedido
Diante do exposto, requer a reintegração de posse...
""",
        "estilo": """
# Estilo de Redação Jurídica

Use linguagem formal, impessoal e técnica...
""",
        "formatacao": """
# Fragmentos de Formatação

## Endereçamento
EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO...
""",
    }


# -----------------------------------------------------------------------------
# Helpers de teste
# -----------------------------------------------------------------------------

@pytest.fixture
def assert_json_valid():
    """Retorna uma função para validar JSON."""
    import json
    
    def _assert_json_valid(text: str) -> dict:
        """Valida se o texto é um JSON válido e retorna o dict."""
        try:
            # Remove markdown se presente
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()
            return json.loads(text)
        except json.JSONDecodeError as exc:
            pytest.fail(f"JSON inválido: {exc}")
    
    return _assert_json_valid
