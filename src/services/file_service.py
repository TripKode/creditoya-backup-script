"""
File Service - Operaciones con archivos locales
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple
import logging


class FileService:
    """
    Servicio para operaciones de archivos locales
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Inicializa el servicio de archivos

        Args:
            logger: Logger opcional para registro de operaciones
        """
        self.logger = logger or logging.getLogger(__name__)

    def copy_folder(self, source_path: str, temp_dir: Optional[str] = None) -> str:
        """
        Crea una copia temporal de la carpeta

        Args:
            source_path: Ruta de la carpeta origen
            temp_dir: Directorio temporal (opcional)

        Returns:
            Ruta de la copia temporal

        Raises:
            FileNotFoundError: Si la carpeta origen no existe
            PermissionError: Si no hay permisos para copiar
        """
        source = Path(source_path)

        if not source.exists():
            raise FileNotFoundError(f"La carpeta origen no existe: {source_path}")

        if not source.is_dir():
            raise ValueError(f"La ruta no es una carpeta: {source_path}")

        # Crear directorio temporal si no se especifica
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp()

        folder_name = source.name
        destination = Path(temp_dir) / folder_name

        self.logger.info(f"Copiando {source_path} a {destination}...")

        try:
            shutil.copytree(source, destination)
            self.logger.info("Copia local completada")
            return str(destination)
        except Exception as e:
            self.logger.error(f"Error al copiar carpeta: {e}")
            raise

    def get_files_to_upload(self, local_folder_path: str) -> List[Tuple[str, str]]:
        """
        Obtiene la lista de archivos a subir desde una carpeta

        Args:
            local_folder_path: Ruta de la carpeta local

        Returns:
            Lista de tuplas (ruta_completa, ruta_relativa)
        """
        folder = Path(local_folder_path)
        files_to_upload = []

        for root, dirs, files in os.walk(folder):
            for file in files:
                local_file = Path(root) / file
                relative_path = local_file.relative_to(folder)
                files_to_upload.append((str(local_file), str(relative_path)))

        self.logger.info(f"Encontrados {len(files_to_upload)} archivos para subir")
        return files_to_upload

    def cleanup_temp(self, temp_path: str) -> None:
        """
        Limpia archivos temporales

        Args:
            temp_path: Ruta del directorio temporal a limpiar
        """
        try:
            temp_dir = Path(temp_path).parent
            self.logger.info("Limpiando archivos temporales...")
            shutil.rmtree(temp_dir)
            self.logger.info("Limpieza completada")
        except Exception as e:
            self.logger.error(f"Error al limpiar archivos temporales: {e}")
            raise

    def get_folder_size(self, folder_path: str) -> int:
        """
        Calcula el tamaño total de una carpeta en bytes

        Args:
            folder_path: Ruta de la carpeta

        Returns:
            Tamaño en bytes
        """
        total_size = 0
        folder = Path(folder_path)

        for item in folder.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size

        return total_size

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Formatea un tamaño en bytes a formato legible

        Args:
            size_bytes: Tamaño en bytes

        Returns:
            Tamaño formateado (ej: "1.5 GB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
