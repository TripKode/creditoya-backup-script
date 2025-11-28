"""
GCS Service - Operaciones con Google Cloud Storage
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple
import logging
from google.cloud import storage
from tqdm import tqdm


class GCSService:
    """
    Servicio para operaciones con Google Cloud Storage
    """

    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Inicializa el servicio de GCS

        Args:
            bucket_name: Nombre del bucket en GCS
            credentials_path: Ruta al archivo de credenciales JSON (opcional)
            logger: Logger opcional para registro de operaciones

        Raises:
            ValueError: Si el bucket_name está vacío
        """
        if not bucket_name:
            raise ValueError("bucket_name no puede estar vacío")

        self.logger = logger or logging.getLogger(__name__)

        # Configurar credenciales si se proporcionan
        if credentials_path:
            if not Path(credentials_path).exists():
                raise FileNotFoundError(f"Archivo de credenciales no encontrado: {credentials_path}")
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            self.logger.info(f"Usando credenciales desde: {credentials_path}")

        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(bucket_name)
            self.logger.info(f"Conectado al bucket: {bucket_name}")
        except Exception as e:
            self.logger.error(f"Error al conectar con GCS: {e}")
            raise

    def upload_files(self, files_to_upload: List[Tuple[str, str]],
                    gcs_folder_name: str, show_progress: bool = True) -> int:
        """
        Sube múltiples archivos a GCS

        Args:
            files_to_upload: Lista de tuplas (ruta_local, ruta_relativa)
            gcs_folder_name: Nombre de la carpeta base en GCS
            show_progress: Mostrar barra de progreso

        Returns:
            Número de archivos subidos exitosamente
        """
        self.logger.info(f"Iniciando subida de {len(files_to_upload)} archivos a GCS...")

        uploaded_count = 0
        failed_files = []

        # Configurar iterador con o sin barra de progreso
        iterator = tqdm(files_to_upload, desc="Subiendo archivos") if show_progress else files_to_upload

        for local_file, relative_path in iterator:
            try:
                blob_name = f"{gcs_folder_name}/{relative_path}".replace("\\", "/")
                blob = self.bucket.blob(blob_name)
                blob.upload_from_filename(local_file)
                uploaded_count += 1
            except Exception as e:
                self.logger.error(f"Error al subir {local_file}: {e}")
                failed_files.append((local_file, str(e)))

        if failed_files:
            self.logger.warning(f"Fallaron {len(failed_files)} archivos:")
            for file, error in failed_files:
                self.logger.warning(f"  - {file}: {error}")

        self.logger.info(f"Subida completada: {uploaded_count}/{len(files_to_upload)} archivos")
        return uploaded_count

    def upload_single_file(self, local_file: str, gcs_path: str) -> bool:
        """
        Sube un solo archivo a GCS

        Args:
            local_file: Ruta del archivo local
            gcs_path: Ruta destino en GCS

        Returns:
            True si se subió exitosamente
        """
        try:
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_filename(local_file)
            self.logger.info(f"Archivo subido: {gcs_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error al subir {local_file}: {e}")
            return False

    def file_exists(self, gcs_path: str) -> bool:
        """
        Verifica si un archivo existe en GCS

        Args:
            gcs_path: Ruta del archivo en GCS

        Returns:
            True si el archivo existe
        """
        blob = self.bucket.blob(gcs_path)
        return blob.exists()

    def list_files(self, prefix: str = "") -> List[str]:
        """
        Lista archivos en el bucket con un prefijo dado

        Args:
            prefix: Prefijo para filtrar archivos

        Returns:
            Lista de nombres de archivos
        """
        blobs = self.client.list_blobs(self.bucket.name, prefix=prefix)
        return [blob.name for blob in blobs]

    def delete_file(self, gcs_path: str) -> bool:
        """
        Elimina un archivo de GCS

        Args:
            gcs_path: Ruta del archivo en GCS

        Returns:
            True si se eliminó exitosamente
        """
        try:
            blob = self.bucket.blob(gcs_path)
            blob.delete()
            self.logger.info(f"Archivo eliminado: {gcs_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error al eliminar {gcs_path}: {e}")
            return False
