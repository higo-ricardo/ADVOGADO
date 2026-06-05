"""
text_normalization.py — Utilitários de normalização de texto para evitar erros de encoding.
Centraliza toute a lógica de ascii/utf-8 aqui para não espalhar try/except pelo app.

Este módulo substitui o antigo text_utils.py com melhor organização.
"""
from __future__ import annotations

import unicodedata
from typing import Union


def normalize_ascii_safe(value: Union[str, bytes, object]) -> str:
    """
    Converte qualquer valor para str ASCII-safe.
    - Remove/transforma acentos e caracteres fora do ASCII.
    - Nunca levanta UnicodeEncodeError/UnicodeDecodeError.
    - Fallback final: repr() se str() falhar.
    """
    try:
        if isinstance(value, bytes):
            text = value.decode("utf-8", errors="replace")
        else:
            text = str(value)
    except Exception:
        return repr(value)

    # Normaliza para NFD (separa acentos) e remove marcas de diacríticos
    try:
        nfkd = unicodedata.normalize("NFKD", text)
        ascii_only = "".join(c for c in nfkd if ord(c) < 128)
        return ascii_only if ascii_only else text
    except Exception:
        return text


def normalize_utf8_strict(value: Union[str, bytes, object]) -> str:
    """
    Garante que a string final é str UTF-8 válida,
    substituindo bytes inválidos pelo caractere de substituição U+FFFD.
    """
    try:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        s = str(value)
        s = s.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
        return s
    except Exception:
        return repr(value)
