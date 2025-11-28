"""
Settings - Configuración de la aplicación
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Settings:
    """
    Configuración de la aplicación
    Puede cargar valores desde variables de entorno o valores por defecto
    """

    # Google Cloud Storage
    bucket_name: str
    credentials_path: Optional[str] = None

    # Rutas
    source_folder: str = "/u/uno"
    gcs_folder_name: str = "external_server_backup/uno_backup"

    # Opciones
    keep_temp: bool = False
    log_level: str = "INFO"
    log_file: Optional[str] = None

    @classmethod
    def from_env(cls) -> 'Settings':
        """
        Crea una instancia de Settings desde variables de entorno

        Variables de entorno:
            GCS_BUCKET_NAME: Nombre del bucket
            GCS_CREDENTIALS_PATH: Ruta a credenciales JSON
            SOURCE_FOLDER: Carpeta origen
            GCS_FOLDER_NAME: Nombre de la carpeta en GCS
            KEEP_TEMP: Mantener archivos temporales (true/false)
            LOG_LEVEL: Nivel de logging (INFO, DEBUG, etc.)
            LOG_FILE: Ruta del archivo de log
        """
        return cls(
            bucket_name=os.getenv('GCS_BUCKET_NAME', ''),
            credentials_path=os.getenv('GCS_CREDENTIALS_PATH'),
            source_folder=os.getenv('SOURCE_FOLDER', '/u/uno'),
            gcs_folder_name=os.getenv('GCS_FOLDER_NAME', 'external_server_backup/uno_backup'),
            keep_temp=os.getenv('KEEP_TEMP', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_file=os.getenv('LOG_FILE')
        )

    def validate(self) -> bool:
        """
        Valida que la configuración sea correcta

        Returns:
            True si la configuración es válida

        Raises:
            ValueError: Si falta alguna configuración requerida
        """
        if not self.bucket_name:
            raise ValueError("bucket_name es requerido")

        if self.credentials_path and not Path(self.credentials_path).exists():
            raise ValueError(f"El archivo de credenciales no existe: {self.credentials_path}")

        if not Path(self.source_folder).exists():
            raise ValueError(f"La carpeta origen no existe: {self.source_folder}")

        return True
