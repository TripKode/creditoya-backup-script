"""
Logger utility - Configuración del sistema de logging
"""

import logging
import sys
from pathlib import Path


def setup_logger(name: str = "creditoya_backup", level: int = logging.INFO, log_file: str = None) -> logging.Logger:
    """
    Configura y retorna un logger para la aplicación

    Args:
        name: Nombre del logger
        level: Nivel de logging (default: INFO)
        log_file: Ruta del archivo de log (opcional)

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar duplicar handlers
    if logger.handlers:
        return logger

    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para archivo (opcional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
