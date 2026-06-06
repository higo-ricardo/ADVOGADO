"""Repositórios para acesso a dados do banco de dados."""

from data.repositories.case_repository import CaseRepository, Case
from data.repositories.document_repository import DocumentRepository, Document
from data.repositories.verbetes_repository import VerbetesRepository
from data.repositories.knowledge_repository import KnowledgeRepository

__all__ = [
    'CaseRepository',
    'Case',
    'DocumentRepository',
    'Document',
    'VerbetesRepository',
    'KnowledgeRepository'
]
