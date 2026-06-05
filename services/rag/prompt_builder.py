"""
prompt_builder.py — Construção de prompts para RAG.
Monta prompts otimizados para geração de peças jurídicas.
"""
from __future__ import annotations

import json
from typing import Any

from infrastructure.config import config
from utils.text_normalization import normalize_utf8_strict


class RAGPromptBuilder:
    """
    Construtor de prompts para RAG.
    
    Responsabilidades:
    - Montar contexto com trechos recuperados
    - Formatar dados do caso
    - Criar instruções específicas por tipo de peça
    """
    
    def __init__(self, top_k: int | None = None):
        """
        Inicializa o construtor de prompts.
        
        Args:
            top_k: Número de trechos a incluir no prompt
        """
        self.top_k = top_k or config.RAG_TOP_K
    
    def build_contract_prompt(
        self,
        descricao_caso: str,
        dominio: str,
        dominio_nome: str,
        codigo: str,
        codigo_nome: str,
        modo: str,
        dados_coletados: dict[str, Any],
    ) -> str:
        """
        Monta prompt para geração de contrato/briefing.
        
        Args:
            descricao_caso: Descrição do caso
            dominio: ID do domínio
            dominio_nome: Nome do domínio
            codigo: Código da peça
            codigo_nome: Nome da peça
            modo: Modo de operação
            dados_coletados: Dados já coletados
        
        Returns:
            Prompt formatado
        """
        prompt = f"""
Com base nos dados abaixo, gere o contrato_decisao no formato JSON.
Responda SOMENTE com o JSON, sem texto adicional, sem markdown.

DADOS DO CASO:
- Descrição: {normalize_utf8_strict(descricao_caso)}
- Domínio: {normalize_utf8_strict(dominio)} — {normalize_utf8_strict(dominio_nome)}
- Código da peça: {normalize_utf8_strict(codigo)} — {normalize_utf8_strict(codigo_nome)}
- Modo: {normalize_utf8_strict(modo)}
- Dados coletados:
{json.dumps(dados_coletados, ensure_ascii=False, indent=2)}

CAMPOS OBRIGATÓRIOS DO JSON:
{{
  "escopo": "resumo dos fatos e tipo de peça",
  "tipo_peca": "{codigo} — {codigo_nome}",
  "dominio": "{dominio} — {dominio_nome}",
  "modo": "{modo}",
  "pedidos": ["pedido 1", "pedido 2"],
  "criterios_aceite": ["critério 1", "critério 2"],
  "regras_criticas": ["regra crítica específica do código {codigo}"],
  "dados": {json.dumps(dados_coletados, ensure_ascii=False)},
  "dependencias": ["fontes.md", "verbetesSTJ.md"],
  "observacoes": "observações adicionais do advogado"
}}
""".strip()
        
        return prompt
    
    def build_document_prompt(
        self,
        descricao_caso: str,
        dominio: str,
        dominio_nome: str,
        codigo: str,
        codigo_nome: str,
        modo: str,
        dados_coletados: dict[str, Any],
        context_trechos: list[dict[str, Any]],
    ) -> str:
        """
        Monta prompt para geração de documento jurídico com RAG.
        
        Args:
            descricao_caso: Descrição do caso
            dominio: ID do domínio
            dominio_nome: Nome do domínio
            codigo: Código da peça
            codigo_nome: Nome da peça
            modo: Modo de operação
            dados_coletados: Dados já coletados
            context_trechos: Lista de trechos recuperados do RAG
        
        Returns:
            Prompt formatado com contexto
        """
        # Formata trechos do RAG
        contexto_rag = "\n\n".join(
            f"[Trecho {i+1}]\n{t['texto']}"
            for i, t in enumerate(context_trechos)
        ) if context_trechos else "[Nenhum trecho relevante encontrado]"
        
        prompt = f"""You are a Brazilian legal assistant. Reply in Brazilian Portuguese.

Use the reference trechos below to draft the procedural document. If a trecho is incomplete or has [A PREENCHER], keep it.

CONTEXTUAL REFERENCE (most relevant trechos from the knowledge base):
{contexto_rag}

CASE DATA:
- Description: {normalize_utf8_strict(descricao_caso)}
- Domain: {normalize_utf8_strict(dominio)} - {normalize_utf8_strict(dominio_nome)}
- Document code: {normalize_utf8_strict(codigo)} - {normalize_utf8_strict(codigo_nome)}
- Mode: {normalize_utf8_strict(modo)}
- Collected data: {json.dumps(dados_coletados, ensure_ascii=False, indent=2)}

Return a complete procedural document following the reference structure.
Include:
1. The complete formatted document
2. A "## CHECKLIST DE ADERENCIA" block with verified items
3. A "## PENDENCIAS" block with any remaining [A PREENCHER] fields.
""".strip()
        
        return prompt
    
    def build_delta_prompt(
        self,
        peca_atual: str,
        instrucao_delta: str,
        contrato: dict[str, Any],
    ) -> str:
        """
        Monta prompt para aplicar modificações (delta) em uma peça.
        
        Args:
            peca_atual: Texto atual da peça
            instrucao_delta: Instrução de modificação
            contrato: Contrato/briefing com contexto
        
        Returns:
            Prompt formatado
        """
        prompt = f"""You are a Brazilian legal assistant. Reply in Brazilian Portuguese always.

Apply the delta below to the procedural document. Change ONLY the indicated section.
Preserve everything not mentioned. Return the full corrected document.

DELTA INSTRUCTION:
{normalize_utf8_strict(instrucao_delta)}

CURRENT CONTRACT:
{json.dumps(contrato, ensure_ascii=False, indent=2)}

CURRENT DOCUMENT:
{normalize_utf8_strict(peca_atual)}
""".strip()
        
        return prompt
