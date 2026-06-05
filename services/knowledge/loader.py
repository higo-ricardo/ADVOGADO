"""
loader.py — Carregamento de arquivos de conhecimento.
Carrega arquivos .md da base de conhecimento.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict

from infrastructure.config import config
from infrastructure.exceptions import KnowledgeError
from utils.text_normalization import normalize_utf8_strict


class KnowledgeLoader:
    """
    Carregador de arquivos de conhecimento.
    
    Responsabilidades:
    - Ler arquivos .md da knowledge base
    - Normalizar texto UTF-8
    - Cache opcional de conteúdo
    """
    
    def __init__(self, knowledge_dir: str | None = None):
        """
        Inicializa o carregador.
        
        Args:
            knowledge_dir: Diretório da base de conhecimento
        """
        self.knowledge_dir = Path(knowledge_dir) if knowledge_dir else config.KNOWLEDGE_DIR
        self._cache: dict[str, str] = {}
    
    def _ler_arquivo(self, nome: str, use_cache: bool = True) -> str:
        """
        Lê um arquivo da base de conhecimento.
        
        Args:
            nome: Nome relativo do arquivo
            use_cache: Se True, usa cache se disponível
        
        Returns:
            Conteúdo normalizado do arquivo
        """
        if use_cache and nome in self._cache:
            return self._cache[nome]
        
        caminho = self.knowledge_dir / nome
        
        if not caminho.exists():
            raise KnowledgeError(f"Arquivo não encontrado: {caminho}")
        
        try:
            texto = caminho.read_text(encoding="utf-8", errors="replace")
            texto_normalizado = normalize_utf8_strict(texto)
            
            if use_cache:
                self._cache[nome] = texto_normalizado
            
            return texto_normalizado
            
        except Exception as exc:
            raise KnowledgeError(f"Falha ao ler arquivo {nome}: {exc}")
    
    def load(self, nome: str, use_cache: bool = True) -> str:
        """
        Carrega um arquivo de conhecimento.
        
        Args:
            nome: Nome relativo do arquivo
            use_cache: Se True, usa cache
        
        Returns:
            Conteúdo do arquivo
        """
        return self._ler_arquivo(nome, use_cache)
    
    def load_multiple(
        self,
        nomes: list[str],
        separator: str = "\n\n---\n\n",
        use_cache: bool = True,
    ) -> str:
        """
        Carrega múltiplos arquivos e concatena.
        
        Args:
            nomes: Lista de nomes de arquivos
            separator: Separador entre arquivos
            use_cache: Se True, usa cache
        
        Returns:
            Conteúdos concatenados
        """
        conteudos = []
        for nome in nomes:
            conteudos.append(self._ler_arquivo(nome, use_cache))
        return separator.join(conteudos)
    
    def load_all_from_directory(
        self,
        subdirectory: str | None = None,
        pattern: str = "*.md",
    ) -> dict[str, str]:
        """
        Carrega todos os arquivos .md de um diretório.
        
        Args:
            subdirectory: Subdiretório opcional
            pattern: Pattern glob para arquivos
        
        Returns:
            Dict {nome_arquivo: conteudo}
        """
        base_dir = self.knowledge_dir
        if subdirectory:
            base_dir = base_dir / subdirectory
        
        resultados: dict[str, str] = {}
        
        for arquivo in sorted(base_dir.rglob(pattern)):
            try:
                relative_path = arquivo.relative_to(self.knowledge_dir)
                conteudo = self._ler_arquivo(str(relative_path))
                resultados[str(relative_path)] = conteudo
            except Exception:
                continue
        
        return resultados
    
    def clear_cache(self) -> None:
        """Limpa o cache de arquivos."""
        self._cache.clear()
    
    def get_cached_files(self) -> list[str]:
        """Retorna lista de arquivos em cache."""
        return list(self._cache.keys())
