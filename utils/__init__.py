"""
utils — Utilitários do Agente Jurídico.
"""
from utils.text_normalization import normalize_ascii_safe, normalize_utf8_strict
from utils.input_validation import (
    validate_input,
    validate_description,
    validate_nome,
    validate_email,
    validate_campo_personalizado,
    check_xss,
    sanitize_html,
    ValidationResult,
    ValidationSeverity,
)

__all__ = [
    "normalize_ascii_safe",
    "normalize_utf8_strict",
    "validate_input",
    "validate_description",
    "validate_nome",
    "validate_email",
    "validate_campo_personalizado",
    "check_xss",
    "sanitize_html",
    "ValidationResult",
    "ValidationSeverity",
]
