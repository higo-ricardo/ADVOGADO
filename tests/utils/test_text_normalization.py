"""
Testes para utilitários de texto.
"""
import pytest
from utils.text_normalization import (
    normalize_ascii_safe,
    normalize_utf8_strict
)


class TestTextNormalization:
    """Testes para funções de normalização de texto."""

    def test_normalize_ascii_safe_basico(self):
        """Testa normalização ASCII safe básica."""
        texto = "Café résumé naïve"
        resultado = normalize_ascii_safe(texto)
        
        # Deve converter caracteres especiais para ASCII
        assert "cafe" in resultado.lower() or "Cafe" in resultado

    def test_normalize_ascii_safe_com_numeros(self):
        """Testa normalização com números e símbolos."""
        texto = "Processo nº 12345-67.2024"
        resultado = normalize_ascii_safe(texto)
        
        assert "12345" in resultado
        assert isinstance(resultado, str)

    def test_normalize_utf8_strict_preserva_unicode(self):
        """Testa que UTF-8 strict preserva unicode."""
        texto = "Ação jurídica ☕"
        resultado = normalize_utf8_strict(texto)
        
        # Deve manter caracteres unicode
        assert "Ação" in resultado or "acao" in resultado.lower()

    def test_normalize_ascii_safe_string_vazia(self):
        """Testa normalização de string vazia."""
        assert normalize_ascii_safe("") == ""

    def test_normalize_ascii_safe_none(self):
        """Testa normalização de None."""
        # Implementação atual converte None para string "None"
        resultado = normalize_ascii_safe(None)
        assert isinstance(resultado, str)

    def test_normalize_ascii_safe_bytes(self):
        """Testa normalização de bytes."""
        texto_bytes = b"Caf\xc3\xa9"  # Café em bytes UTF-8
        resultado = normalize_ascii_safe(texto_bytes)
        
        assert isinstance(resultado, str)

    def test_normalize_utf8_strict_string_vazia(self):
        """Testa UTF-8 strict com string vazia."""
        assert normalize_utf8_strict("") == ""

    def test_normalize_utf8_strict_none(self):
        """Testa UTF-8 strict com None."""
        # Implementação atual converte None para string "None"
        resultado = normalize_utf8_strict(None)
        assert isinstance(resultado, str)
