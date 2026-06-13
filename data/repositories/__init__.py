"""Repositórios para acesso a dados do banco de dados."""

from data.repositories.case_repository import CaseRepository, Case
from data.repositories.document_repository import DocumentRepository, Document

__all__ = [
    'CaseRepository',
    'Case',
    'DocumentRepository',
    'Document',
]
