"""
tests/services/rag/test_indexer.py — Testes do indexador de documentos.
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from infrastructure.exceptions import RAGError
from services.rag.indexer import DocumentIndexer


class TestDocumentIndexer:
    """Testes da classe DocumentIndexer."""
    
    @patch('services.rag.indexer.config')
    def test_initialization_with_defaults(self, mock_config):
        """Inicialização usa valores default da config."""
        mock_config.RAG_MODEL_NAME = "test-model"
        mock_config.RAG_CHUNK_SIZE = 500
        mock_config.RAG_CHUNK_OVERLAP = 50
        
        indexer = DocumentIndexer()
        
        assert indexer.model_name == "test-model"
        assert indexer.chunk_size == 500
        assert indexer.chunk_overlap == 50
        assert indexer.is_indexed is False
    
    @patch('services.rag.indexer.config')
    def test_initialization_with_custom_params(self, mock_config):
        """Inicialização com parâmetros customizados sobrescreve defaults."""
        mock_config.RAG_MODEL_NAME = "default-model"
        
        indexer = DocumentIndexer(
            model_name="custom-model",
            chunk_size=1000,
            chunk_overlap=100,
        )
        
        assert indexer.model_name == "custom-model"
        assert indexer.chunk_size == 1000
        assert indexer.chunk_overlap == 100
    
    @patch('services.rag.indexer.SentenceTransformer')
    @patch('services.rag.indexer.config')
    def test_load_model_caches(self, mock_config, mock_transformer):
        """Modelo é carregado apenas uma vez (cache)."""
        mock_config.RAG_MODEL_NAME = "test-model"
        mock_model_instance = Mock()
        mock_transformer.return_value = mock_model_instance
        
        indexer = DocumentIndexer()
        
        # Primeira chamada
        indexer._load_model()
        # Segunda chamada
        indexer._load_model()
        
        # Modelo deve ser instanciado apenas uma vez
        mock_transformer.assert_called_once_with("test-model")
    
    @patch('services.rag.indexer.SentenceTransformer')
    @patch('services.rag.indexer.config')
    def test_load_model_error_raises_ragerror(self, mock_config, mock_transformer):
        """Erro ao carregar modelo lança RAGError."""
        mock_config.RAG_MODEL_NAME = "test-model"
        mock_transformer.side_effect = Exception("Model load failed")
        
        indexer = DocumentIndexer()
        
        with pytest.raises(RAGError, match="Falha ao carregar modelo"):
            indexer._load_model()
    
    @patch('services.rag.indexer.config')
    def test_chunk_text_splits_correctly(self, mock_config):
        """Chunking divide texto corretamente com sobreposição."""
        mock_config.RAG_MODEL_NAME = "test-model"
        mock_config.RAG_CHUNK_SIZE = 5
        mock_config.RAG_CHUNK_OVERLAP = 2
        
        indexer = DocumentIndexer(chunk_size=5, chunk_overlap=2)
        text = "one two three four five six seven eight nine ten"
        
        chunks = indexer._chunk_text(text)
        
        # Deve criar chunks com 5 palavras e sobreposição de 2
        assert len(chunks) > 1
        assert all(len(chunk.split()) <= 5 for chunk in chunks)
    
    @patch('services.rag.indexer.config')
    def test_chunk_text_empty_returns_empty_list(self, mock_config):
        """Texto vazio retorna lista vazia."""
        mock_config.RAG_MODEL_NAME = "test-model"
        
        indexer = DocumentIndexer()
        
        assert indexer._chunk_text("") == []
        assert indexer._chunk_text("   ") == []
    
    @patch('services.rag.indexer.SentenceTransformer')
    @patch('services.rag.indexer.config')
    def test_index_documents_success(self, mock_config, mock_transformer):
        """Indexação de documentos funciona corretamente."""
        mock_config.RAG_MODEL_NAME = "test-model"
        mock_config.RAG_CHUNK_SIZE = 500
        mock_config.RAG_CHUNK_OVERLAP = 50
        mock_model_instance = Mock()
        mock_model_instance.encode.return_value = np.random.rand(2, 384)
        mock_transformer.return_value = mock_model_instance
        
        indexer = DocumentIndexer()
        documents = {
            "doc1": "content one two three",
            "doc2": "content four five six",
        }
        
        count = indexer.index_documents(documents)
        
        assert count > 0
        assert indexer.is_indexed is True
        assert indexer.vector_count == count
    
    @patch('services.rag.indexer.SentenceTransformer')
    @patch('services.rag.indexer.config')
    def test_index_documents_empty_content(self, mock_config, mock_transformer):
        """Documentos vazios não geram chunks."""
        mock_config.RAG_MODEL_NAME = "test-model"
        mock_config.RAG_CHUNK_SIZE = 500
        mock_config.RAG_CHUNK_OVERLAP = 50
        
        indexer = DocumentIndexer()
        documents = {"doc1": "", "doc2": "   "}
        
        count = indexer.index_documents(documents)
        
        assert count == 0
        assert indexer.is_indexed is True
        assert indexer.vector_count == 0
    
    @patch('services.rag.indexer.SentenceTransformer')
    @patch('services.rag.indexer.config')
    def test_index_documents_skip_if_already_indexed(self, mock_config, mock_transformer):
        """Indexação é pulada se já estiver indexado (sem force_rebuild)."""
        mock_config.RAG_MODEL_NAME = "test-model"
        mock_config.RAG_CHUNK_SIZE = 500
        mock_config.RAG_CHUNK_OVERLAP = 50
        mock_model_instance = Mock()
        mock_model_instance.encode.return_value = np.random.rand(1, 384)
        mock_transformer.return_value = mock_model_instance
        
        indexer = DocumentIndexer()
        documents1 = {"doc1": "content"}
        documents2 = {"doc2": "other content"}
        
        # Primeira indexação
        indexer.index_documents(documents1)
        initial_count = indexer.vector_count
        
        # Segunda indexação sem force_rebuild
        indexer.index_documents(documents2)
        
        # Contagem deve permanecer a mesma
        assert indexer.vector_count == initial_count
    
    @patch('services.rag.indexer.SentenceTransformer')
    @patch('services.rag.indexer.config')
    def test_index_documents_force_rebuild(self, mock_config, mock_transformer):
        """force_rebuild=True reconstrói o índice."""
        mock_config.RAG_MODEL_NAME = "test-model"
        mock_config.RAG_CHUNK_SIZE = 500
        mock_config.RAG_CHUNK_OVERLAP = 50
        mock_model_instance = Mock()
        mock_model_instance.encode.side_effect = [
            np.random.rand(1, 384),  # Primeira indexação
            np.random.rand(2, 384),  # Rebuild
        ]
        mock_transformer.return_value = mock_model_instance
        
        indexer = DocumentIndexer()
        documents1 = {"doc1": "content"}
        documents2 = {"doc2": "other content", "doc3": "more content"}
        
        # Primeira indexação
        indexer.index_documents(documents1)
        initial_count = indexer.vector_count
        
        # Rebuild com force_rebuild
        indexer.index_documents(documents2, force_rebuild=True)
        
        # Contagem deve mudar
        assert indexer.vector_count != initial_count
    
    @patch('services.rag.indexer.SentenceTransformer')
    @patch('services.rag.indexer.config')
    def test_index_documents_encoding_error_raises_ragerror(self, mock_config, mock_transformer):
        """Erro ao criar embeddings lança RAGError."""
        mock_config.RAG_MODEL_NAME = "test-model"
        mock_config.RAG_CHUNK_SIZE = 500
        mock_config.RAG_CHUNK_OVERLAP = 50
        mock_model_instance = Mock()
        mock_model_instance.encode.side_effect = Exception("Encoding failed")
        mock_transformer.return_value = mock_model_instance
        
        indexer = DocumentIndexer()
        documents = {"doc1": "content"}
        
        with pytest.raises(RAGError, match="Falha ao criar embeddings"):
            indexer.index_documents(documents)
    
    @patch('services.rag.indexer.SentenceTransformer')
    @patch('services.rag.indexer.config')
    def test_reset_clears_index(self, mock_config, mock_transformer):
        """Reset limpa todos os dados do índice."""
        mock_config.RAG_MODEL_NAME = "test-model"
        mock_config.RAG_CHUNK_SIZE = 500
        mock_config.RAG_CHUNK_OVERLAP = 50
        mock_model_instance = Mock()
        mock_model_instance.encode.return_value = np.random.rand(1, 384)
        mock_transformer.return_value = mock_model_instance
        
        indexer = DocumentIndexer()
        indexer.index_documents({"doc1": "content"})
        
        assert indexer.is_indexed is True
        assert indexer.vector_count > 0
        
        indexer.reset()
        
        assert indexer.is_indexed is False
        assert indexer.vector_count == 0
        assert indexer.vectors is None
        assert indexer.ids == []
        assert indexer.textos == []
    
    @patch('services.rag.indexer.SentenceTransformer')
    @patch('services.rag.indexer.config')
    def test_properties_return_correct_values(self, mock_config, mock_transformer):
        """Propriedades retornam valores corretos após indexação."""
        mock_config.RAG_MODEL_NAME = "test-model"
        mock_config.RAG_CHUNK_SIZE = 500
        mock_config.RAG_CHUNK_OVERLAP = 50
        mock_model_instance = Mock()
        mock_vectors = np.random.rand(2, 384)
        mock_model_instance.encode.return_value = mock_vectors
        mock_transformer.return_value = mock_model_instance
        
        indexer = DocumentIndexer()
        indexer.index_documents({
            "doc1": "content one",
            "doc2": "content two",
        })
        
        assert indexer.vectors is not None
        assert len(indexer.vectors) == 2
        assert len(indexer.ids) == 2
        assert len(indexer.textos) == 2
        assert all("doc1::" in id or "doc2::" in id for id in indexer.ids)
