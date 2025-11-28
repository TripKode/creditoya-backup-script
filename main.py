"""
Creditoya Backup - Sistema de backup a Google Cloud Storage

Este script permite hacer backup de carpetas locales a Google Cloud Storage.
Puede configurarse mediante variables de entorno o parámetros directos.
"""

import sys
import logging
from pathlib import Path

from src.core.uploader import FolderUploader
from src.config.settings import Settings
from src.utils.logger import setup_logger


def main():
    """
    Función principal del script de backup
    """
    # Configurar logging
    logger = setup_logger(
        name="creditoya_backup",
        level=logging.INFO
    )

    try:
        logger.info("=" * 60)
        logger.info("Creditoya Backup - Iniciando proceso")
        logger.info("=" * 60)

        # Opción 1: Cargar configuración desde variables de entorno
        # settings = Settings.from_env()

        # Opción 2: Configuración manual (descomentar y ajustar según necesites)
        settings = Settings(
            bucket_name="tu-bucket-name",
            credentials_path="credentials/tu-credenciales.json",  # Opcional
            source_folder="/u/uno",
            gcs_folder_name="external_server_backup/uno_backup",
            keep_temp=False,
            log_level="INFO"
        )

        # Crear instancia del uploader
        uploader = FolderUploader(settings=settings, logger=logger)

        # Ejecutar proceso completo
        result = uploader.process_and_upload()

        # Verificar resultado
        if result['success']:
            logger.info("=" * 60)
            logger.info(f"✓ Backup completado exitosamente")
            logger.info(f"  Archivos subidos: {result['files_uploaded']}")
            logger.info("=" * 60)
            return 0
        else:
            logger.error("=" * 60)
            logger.error("✗ El backup no se completó correctamente")
            if result['error']:
                logger.error(f"  Error: {result['error']}")
            logger.error("=" * 60)
            return 1

    except ValueError as e:
        logger.error(f"Error de configuración: {e}")
        logger.error("Verifica tu configuración y vuelve a intentar")
        return 1

    except KeyboardInterrupt:
        logger.warning("\nProceso interrumpido por el usuario")
        return 130

    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
