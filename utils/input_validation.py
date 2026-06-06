"""
utils/input_validation.py — Validação de inputs do usuário.
Proteção contra XSS, validação de tamanho e caracteres.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ValidationSeverity(Enum):
    """Nível de severidade do erro de validação."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Resultado de uma validação."""
    is_valid: bool
    message: str = ""
    severity: ValidationSeverity = ValidationSeverity.ERROR
    sanitized_value: Optional[str] = None


# Padrões de segurança
XSS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # Tags script
    r'javascript:',                # Protocolo javascript
    r'on\w+\s*=',                  # Handlers de eventos (onclick, onerror, etc.)
    r'<iframe[^>]*>',              # iframes
    r'<object[^>]*>',              # objects
    r'<embed[^>]*>',               # embeds
    r'<link[^>]*href\s*=\s*["\']?javascript:',  # Links javascript
    r'expression\s*\(',            # CSS expression
    r'url\s*\(\s*["\']?\s*javascript:',  # URL javascript em CSS
    r'data:\s*text/html',          # Data URI HTML
    r'<\s*/?\s*(?:alert|confirm|prompt)\s*>',  # Funções de alerta
]

# Compila padrões para performance
XSS_REGEX = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in XSS_PATTERNS]

# Caracteres permitidos por tipo de campo
ALLOWED_CHARS = {
    "alphanumeric": re.compile(r'^[\w\s\-.,;:!?()"\']+$', re.UNICODE),
    "text": re.compile(r'^[\w\s\-.,;:!?()"\'áàâãéèêíìîóòôõúùûçñÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇÑ]+$', re.UNICODE),
    "legal": re.compile(r'^[\w\s\-.,;:!?()"\'áàâãéèêíìîóòôõúùûçñÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇÑ§ºª°/\\]+\d*$', re.UNICODE),
    "email": re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
    "phone": re.compile(r'^[\d\s\-\+()]+$'),
    "document": re.compile(r'^[\d.\-/]+$'),  # CPF, CNPJ, RG
}

# Limites de tamanho
SIZE_LIMITS = {
    "description": {"min": 20, "max": 5000},
    "name": {"min": 2, "max": 200},
    "email": {"min": 5, "max": 254},
    "phone": {"min": 10, "max": 20},
    "document": {"min": 11, "max": 18},
    "text_area": {"min": 10, "max": 10000},
    "text_input": {"min": 1, "max": 500},
    "default": {"min": 1, "max": 2000},
}


def check_xss(value: str) -> ValidationResult:
    """
    Verifica se o valor contém padrões XSS maliciosos.
    
    Args:
        value: String a ser validada
    
    Returns:
        ValidationResult com status da validação
    """
    if not value:
        return ValidationResult(is_valid=True)
    
    for regex in XSS_REGEX:
        if regex.search(value):
            return ValidationResult(
                is_valid=False,
                message="Conteúdo potencialmente malicioso detectado",
                severity=ValidationSeverity.CRITICAL,
            )
    
    return ValidationResult(is_valid=True)


def sanitize_html(value: str) -> str:
    """
    Remove tags HTML perigosas mantendo formatação básica segura.
    
    Args:
        value: String com possível HTML
    
    Returns:
        String sanitizada
    """
    if not value:
        return value
    
    # Remove tags script, style, iframe, object, embed
    dangerous_tags = ['script', 'style', 'iframe', 'object', 'embed', 'link', 'meta']
    for tag in dangerous_tags:
        value = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', value, flags=re.IGNORECASE | re.DOTALL)
        value = re.sub(f'<{tag}[^>]*/?>', '', value, flags=re.IGNORECASE)
    
    # Remove handlers de eventos
    value = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
    value = re.sub(r'\s*on\w+\s*=\s*\S+', '', value, flags=re.IGNORECASE)
    
    # Remove javascript: e data:text/html
    value = re.sub(r'javascript:[^"\'>\s]*', '', value, flags=re.IGNORECASE)
    value = re.sub(r'data:\s*text/html[^"\'>\s]*', '', value, flags=re.IGNORECASE)
    
    return value.strip()


def validate_size(
    value: str,
    field_type: str = "default",
    custom_min: Optional[int] = None,
    custom_max: Optional[int] = None,
) -> ValidationResult:
    """
    Valida o tamanho do texto conforme limites configurados.
    
    Args:
        value: String a ser validada
        field_type: Tipo do campo (description, name, text_area, etc.)
        custom_min: Limite mínimo personalizado
        custom_max: Limite máximo personalizado
    
    Returns:
        ValidationResult com status da validação
    """
    if not value:
        return ValidationResult(
            is_valid=False,
            message="Campo vazio não é permitido",
            severity=ValidationSeverity.ERROR,
        )
    
    limits = SIZE_LIMITS.get(field_type, SIZE_LIMITS["default"])
    min_size = custom_min if custom_min is not None else limits["min"]
    max_size = custom_max if custom_max is not None else limits["max"]
    
    length = len(value)
    
    if length < min_size:
        return ValidationResult(
            is_valid=False,
            message=f"Mínimo de {min_size} caracteres necessário (atual: {length})",
            severity=ValidationSeverity.WARNING,
        )
    
    if length > max_size:
        return ValidationResult(
            is_valid=False,
            message=f"Máximo de {max_size} caracteres permitido (atual: {length})",
            severity=ValidationSeverity.ERROR,
            sanitized_value=value[:max_size],
        )
    
    return ValidationResult(is_valid=True)


def validate_characters(
    value: str,
    char_type: str = "text",
    allow_extra: Optional[str] = None,
) -> ValidationResult:
    """
    Valida se o texto contém apenas caracteres permitidos.
    
    Args:
        value: String a ser validada
        char_type: Tipo de caractere permitido (alphanumeric, text, legal, email, phone, document)
        allow_extra: Caracteres extras permitidos além do padrão
    
    Returns:
        ValidationResult com status da validação
    """
    if not value:
        return ValidationResult(is_valid=True)
    
    pattern = ALLOWED_CHARS.get(char_type)
    if pattern is None:
        return ValidationResult(
            is_valid=True,  # Se tipo desconhecido, permite
            message=f"Tipo de caractere '{char_type}' não reconhecido",
            severity=ValidationSeverity.INFO,
        )
    
    if not pattern.match(value):
        # Tenta identificar caracteres problemáticos
        invalid_chars = set(c for c in value if not pattern.match(c))
        if invalid_chars:
            chars_display = ''.join(list(invalid_chars)[:10])
            return ValidationResult(
                is_valid=False,
                message=f"Caracteres não permitidos detectados: {chars_display}",
                severity=ValidationSeverity.WARNING,
            )
        
        return ValidationResult(
            is_valid=False,
            message=f"Formato inválido para campo do tipo '{char_type}'",
            severity=ValidationSeverity.WARNING,
        )
    
    return ValidationResult(is_valid=True)


def validate_input(
    value: str,
    field_type: str = "default",
    char_type: str = "text",
    check_xss_enabled: bool = True,
    custom_min: Optional[int] = None,
    custom_max: Optional[int] = None,
) -> ValidationResult:
    """
    Validação completa de input do usuário.
    
    Args:
        value: Valor a ser validado
        field_type: Tipo do campo para validação de tamanho
        char_type: Tipo de caractere para validação de formato
        check_xss_enabled: Se deve verificar XSS
        custom_min: Limite mínimo personalizado
        custom_max: Limite máximo personalizado
    
    Returns:
        ValidationResult com status completo da validação
    """
    if not isinstance(value, str):
        return ValidationResult(
            is_valid=False,
            message="Valor deve ser uma string",
            severity=ValidationSeverity.ERROR,
        )
    
    # 1. Check XSS (crítico)
    if check_xss_enabled:
        xss_result = check_xss(value)
        if not xss_result.is_valid:
            return xss_result
    
    # 2. Valida tamanho
    size_result = validate_size(
        value,
        field_type=field_type,
        custom_min=custom_min,
        custom_max=custom_max,
    )
    if not size_result.is_valid:
        return size_result
    
    # 3. Valida caracteres (warning, não bloqueante para texto jurídico)
    char_result = validate_characters(value, char_type=char_type)
    if not char_result.is_valid and char_result.severity == ValidationSeverity.ERROR:
        return char_result
    
    # Sanitiza o valor
    sanitized = sanitize_html(value)
    
    return ValidationResult(
        is_valid=True,
        message="Validação bem-sucedida",
        sanitized_value=sanitized,
    )


def validate_description(descricao: str) -> ValidationResult:
    """
    Validação específica para descrição de caso.
    
    Args:
        descricao: Descrição do caso
    
    Returns:
        ValidationResult
    """
    return validate_input(
        value=descricao,
        field_type="description",
        char_type="legal",
        check_xss_enabled=True,
        custom_min=20,
        custom_max=5000,
    )


def validate_nome(nome: str) -> ValidationResult:
    """
    Validação específica para nomes (partes, advogados).
    
    Args:
        nome: Nome a validar
    
    Returns:
        ValidationResult
    """
    return validate_input(
        value=nome,
        field_type="name",
        char_type="text",
        check_xss_enabled=True,
        custom_min=2,
        custom_max=200,
    )


def validate_email(email: str) -> ValidationResult:
    """
    Validação específica para e-mail.
    
    Args:
        email: E-mail a validar
    
    Returns:
        ValidationResult
    """
    # Primeiro valida tamanho básico
    size_result = validate_size(email, field_type="email")
    if not size_result.is_valid:
        return size_result
    
    # Depois valida formato
    email = email.strip()
    pattern = ALLOWED_CHARS["email"]
    
    if not pattern.match(email):
        return ValidationResult(
            is_valid=False,
            message="Formato de e-mail inválido",
            severity=ValidationSeverity.ERROR,
        )
    
    return ValidationResult(is_valid=True, sanitized_value=email)


def validate_campo_personalizado(
    valor: str,
    label: str,
    obrigatorio: bool = True,
    min_chars: int = 1,
    max_chars: int = 500,
    tipo: str = "text",
) -> ValidationResult:
    """
    Validação genérica para campos personalizados.
    
    Args:
        valor: Valor do campo
        label: Rótulo do campo (para mensagens de erro)
        obrigatorio: Se o campo é obrigatório
        min_chars: Mínimo de caracteres
        max_chars: Máximo de caracteres
        tipo: Tipo de validação de caracteres
    
    Returns:
        ValidationResult
    """
    if not valor or not valor.strip():
        if obrigatorio:
            return ValidationResult(
                is_valid=False,
                message=f"Campo '{label}' é obrigatório",
                severity=ValidationSeverity.ERROR,
            )
        return ValidationResult(is_valid=True)
    
    return validate_input(
        value=valor.strip(),
        field_type="default",
        char_type=tipo,
        check_xss_enabled=True,
        custom_min=min_chars,
        custom_max=max_chars,
    )
