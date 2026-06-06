"""
src/application/__init__.py — Camada de Aplicação (Casos de Uso).

Esta camada orquestra os serviços para executar casos de uso específicos,
sem depender de frameworks de UI ou detalhes de infraestrutura.
"""
from __future__ import annotations

from src.application.use_cases import (
    SubmitLegalQueryUseCase,
    ConfirmPieceUseCase,
    CollectDataUseCase,
    GenerateContractUseCase,
    GenerateDocumentUseCase,
    ApplyDeltaUseCase,
    ResetStateUseCase,
)
from src.application.app_facade import AppFacade, create_app_context


__all__ = [
    # Casos de uso
    "SubmitLegalQueryUseCase",
    "ConfirmPieceUseCase",
    "CollectDataUseCase",
    "GenerateContractUseCase",
    "GenerateDocumentUseCase",
    "ApplyDeltaUseCase",
    "ResetStateUseCase",
    # Facade
    "AppFacade",
    "create_app_context",
]
