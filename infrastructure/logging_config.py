"""
logging_config.py — Configuração de logging estruturado.
"""
import logging
import sys
from pathlib import Path


def setup_logging(level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    Configura logging para o agente jurídico.
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR)
        log_file: Caminho opcional para arquivo de log
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger("agente_juridico")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Evita duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formatter padrão
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (opcional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Logger global
logger = setup_logging()
