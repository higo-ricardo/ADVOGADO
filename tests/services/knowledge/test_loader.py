"""
tests/services/knowledge/test_loader.py — Testes do carregador de conhecimento.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from infrastructure.exceptions import KnowledgeError
from services.knowledge.loader import KnowledgeLoader


class TestKnowledgeLoader:
    """Testes da classe KnowledgeLoader."""
    
    @patch('services.knowledge.loader.config')
    def test_initialization_with_default_dir(self, mock_config):
        """Inicialização usa diretório default da config."""
        mock_config.KNOWLEDGE_DIR = Path("/default/knowledge")
        
        loader = KnowledgeLoader()
        
        assert loader.knowledge_dir == Path("/default/knowledge")
        assert loader._cache == {}
    
    @patch('services.knowledge.loader.config')
    def test_initialization_with_custom_dir(self, mock_config):
        """Inicialização com diretório customizado sobrescreve default."""
        mock_config.KNOWLEDGE_DIR = Path("/default/knowledge")
        
        loader = KnowledgeLoader(knowledge_dir="/custom/knowledge")
        
        assert loader.knowledge_dir == Path("/custom/knowledge")
    
    @patch('services.knowledge.loader.config')
    def test_clear_cache(self, mock_config):
        """clear_cache limpa o cache."""
        mock_config.KNOWLEDGE_DIR = Path("/knowledge")
        
        loader = KnowledgeLoader()
        loader._cache = {"file1.md": "content1", "file2.md": "content2"}
        
        loader.clear_cache()
        
        assert loader._cache == {}
        assert loader.get_cached_files() == []
    
    @patch('services.knowledge.loader.config')
    def test_get_cached_files(self, mock_config):
        """get_cached_files retorna lista de arquivos em cache."""
        mock_config.KNOWLEDGE_DIR = Path("/knowledge")
        
        loader = KnowledgeLoader()
        loader._cache = {"file1.md": "content1", "file2.md": "content2"}
        
        cached = loader.get_cached_files()
        
        assert set(cached) == {"file1.md", "file2.md"}
    
    @patch('services.knowledge.loader.normalize_utf8_strict')
    @patch('services.knowledge.loader.config')
    def test_load_file_success(self, mock_config, mock_normalize):
        """Carregamento de arquivo funciona corretamente."""
        mock_config.KNOWLEDGE_DIR = Path("/knowledge")
        mock_normalize.return_value = "normalized content"
        
        # Mock do arquivo
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_file.read_text.return_value = "raw content"
        
        with patch.object(Path, 'read_text', return_value="raw content"):
            with patch.object(Path, 'exists', return_value=True):
                loader = KnowledgeLoader()
                content = loader.load("test.md")
                
                assert content == "normalized content"
                mock_normalize.assert_called_once_with("raw content")
    
    @patch('services.knowledge.loader.config')
    def test_load_file_not_found_raises_error(self, mock_config):
        """Arquivo não encontrado lança KnowledgeError."""
        mock_config.KNOWLEDGE_DIR = Path("/knowledge")
        
        with patch.object(Path, 'exists', return_value=False):
            loader = KnowledgeLoader()
            
            with pytest.raises(KnowledgeError, match="Arquivo não encontrado"):
                loader.load("nonexistent.md")
    
    @patch('services.knowledge.loader.config')
    def test_load_uses_cache(self, mock_config):
        """load usa cache quando disponível."""
        mock_config.KNOWLEDGE_DIR = Path("/knowledge")
        
        loader = KnowledgeLoader()
        loader._cache["cached.md"] = "cached content"
        
        # Não deve tentar ler do disco se está em cache
        with patch.object(Path, 'exists', return_value=True) as mock_exists:
            content = loader.load("cached.md", use_cache=True)
            
            assert content == "cached content"
            mock_exists.assert_not_called()
    
    @patch('services.knowledge.loader.normalize_utf8_strict')
    @patch('services.knowledge.loader.config')
    def test_load_without_cache(self, mock_config, mock_normalize):
        """load sem cache lê do disco mesmo com arquivo em cache."""
        mock_config.KNOWLEDGE_DIR = Path("/knowledge")
        mock_normalize.return_value = "new content"
        
        loader = KnowledgeLoader()
        loader._cache["file.md"] = "old cached content"
        
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value="raw content"):
                content = loader.load("file.md", use_cache=False)
                
                assert content == "new content"
                # Cache não foi atualizado porque use_cache=False no load
                # mas _ler_arquivo pode atualizar se use_cache=True internamente
    
    @patch('services.knowledge.loader.normalize_utf8_strict')
    @patch('services.knowledge.loader.config')
    def test_load_populates_cache(self, mock_config, mock_normalize):
        """load popula cache após leitura."""
        mock_config.KNOWLEDGE_DIR = Path("/knowledge")
        mock_normalize.return_value = "normalized content"
        
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value="raw content"):
                loader = KnowledgeLoader()
                
                assert "new.md" not in loader.get_cached_files()
                
                loader.load("new.md", use_cache=True)
                
                assert "new.md" in loader.get_cached_files()
                assert loader._cache["new.md"] == "normalized content"
    
    @patch('services.knowledge.loader.config')
    def test_load_multiple_concatenates_files(self, mock_config):
        """load_multiple concatena múltiplos arquivos."""
        mock_config.KNOWLEDGE_DIR = Path("/knowledge")
        
        def mock_read(name, use_cache):
            return f"content of {name}"
        
        loader = KnowledgeLoader()
        loader._ler_arquivo = mock_read  # type: ignore
        
        result = loader.load_multiple(["file1.md", "file2.md"], separator=" | ")
        
        assert result == "content of file1.md | content of file2.md"
    
    @patch('services.knowledge.loader.config')
    def test_load_multiple_default_separator(self, mock_config):
        """load_multiple usa separador default."""
        mock_config.KNOWLEDGE_DIR = Path("/knowledge")
        
        def mock_read(name, use_cache):
            return f"content of {name}"
        
        loader = KnowledgeLoader()
        loader._ler_arquivo = mock_read  # type: ignore
        
        result = loader.load_multiple(["file1.md", "file2.md"])
        
        assert "\n\n---\n\n" in result
    
    @patch('services.knowledge.loader.config')
    def test_load_all_from_directory(self, mock_config):
        """load_all_from_directory carrega todos os .md do diretório."""
        import tempfile
        import os
        
        # Usar arquivos reais para teste de integração
        with tempfile.TemporaryDirectory() as tmpdir:
            # Criar estrutura de diretórios
            subdir = os.path.join(tmpdir, 'bbb_subdir')
            os.makedirs(subdir)
            
            # Criar arquivos
            with open(os.path.join(tmpdir, 'aaa_file1.md'), 'w') as f:
                f.write('content1')
            with open(os.path.join(subdir, 'file2.md'), 'w') as f:
                f.write('content2')
            
            loader = KnowledgeLoader(knowledge_dir=tmpdir)
            result = loader.load_all_from_directory()
            
            assert len(result) == 2
            assert "aaa_file1.md" in result
            assert "bbb_subdir/file2.md" in result
    
    @patch('services.knowledge.loader.config')
    def test_load_all_from_directory_with_subdirectory(self, mock_config):
        """load_all_from_directory suporta subdiretório."""
        import tempfile
        import os
        
        mock_config.KNOWLEDGE_DIR = Path("/knowledge")
        
        # Usar arquivos reais para teste de integração
        with tempfile.TemporaryDirectory() as tmpdir:
            # Criar subdiretório
            subdir = os.path.join(tmpdir, 'subdir')
            os.makedirs(subdir)
            
            # Criar arquivo no subdiretório
            with open(os.path.join(subdir, 'file.md'), 'w') as f:
                f.write('content')
            
            loader = KnowledgeLoader(knowledge_dir=tmpdir)
            result = loader.load_all_from_directory(subdirectory="subdir")
            
            # Verifica que o arquivo foi carregado do subdiretório
            assert len(result) == 1
            assert "subdir/file.md" in result
    
    @patch.object(KnowledgeLoader, '_ler_arquivo')
    def test_load_all_from_directory_skips_errors(self, mock_ler):
        """load_all_from_directory ignora arquivos com erro de leitura."""
        import tempfile
        import os
        
        # Usar arquivos reais para teste de integração
        with tempfile.TemporaryDirectory() as tmpdir:
            # Criar arquivos
            with open(os.path.join(tmpdir, 'aaa_good.md'), 'w') as f:
                f.write('good content')
            with open(os.path.join(tmpdir, 'bbb_error.md'), 'w') as f:
                f.write('error content')
            
            loader = KnowledgeLoader(knowledge_dir=tmpdir)
            
            # Configurar mock para falhar em um arquivo específico
            def side_effect(nome, use_cache=True):
                if "bbb_error" in nome:
                    raise Exception("Read error simulado")
                return "good content"
            
            mock_ler.side_effect = side_effect
            
            result = loader.load_all_from_directory()
            
            # Apenas o arquivo sem erro deve estar no resultado
            assert len(result) == 1
            assert any("aaa_good.md" in k for k in result.keys())
            assert not any("bbb_error.md" in k for k in result.keys())
