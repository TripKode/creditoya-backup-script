"""
Folder Uploader - Clase principal para backup de carpetas a GCS
"""

import logging
from typing import Optional
from ..services.file_service import FileService
from ..services.gcs_service import GCSService
from ..config.settings import Settings


class FolderUploader:
    """
    Clase principal para gestionar el backup de carpetas a Google Cloud Storage

    Esta clase orquesta los servicios de archivos y GCS para realizar
    copias de carpetas locales y subirlas a la nube.
    """

    def __init__(self, settings: Settings, logger: Optional[logging.Logger] = None):
        """
        Inicializa el uploader

        Args:
            settings: Configuración de la aplicación
            logger: Logger opcional (se creará uno por defecto si no se proporciona)
        """
        self.settings = settings
        self.logger = logger or logging.getLogger(__name__)

        # Validar configuración
        try:
            self.settings.validate()
        except ValueError as e:
            self.logger.error(f"Error en la configuración: {e}")
            raise

        # Inicializar servicios
        self.file_service = FileService(logger=self.logger)
        self.gcs_service = GCSService(
            bucket_name=self.settings.bucket_name,
            credentials_path=self.settings.credentials_path,
            logger=self.logger
        )

        self.logger.info("FolderUploader inicializado correctamente")

    def copy_folder_local(self, source_path: str, temp_dir: Optional[str] = None) -> str:
        """
        Crea una copia temporal de la carpeta

        Args:
            source_path: Ruta de la carpeta origen
            temp_dir: Directorio temporal (opcional)

        Returns:
            Ruta de la copia temporal
        """
        return self.file_service.copy_folder(source_path, temp_dir)

    def upload_folder_to_gcs(self, local_folder_path: str,
                            gcs_folder_name: Optional[str] = None,
                            show_progress: bool = True) -> int:
        """
        Sube la carpeta completa a Google Cloud Storage

        Args:
            local_folder_path: Ruta de la carpeta local a subir
            gcs_folder_name: Nombre de la carpeta en GCS (opcional)
            show_progress: Mostrar barra de progreso

        Returns:
            Número de archivos subidos exitosamente
        """
        if gcs_folder_name is None:
            import os
            gcs_folder_name = os.path.basename(local_folder_path)

        # Obtener lista de archivos
        files_to_upload = self.file_service.get_files_to_upload(local_folder_path)

        if not files_to_upload:
            self.logger.warning("No hay archivos para subir")
            return 0

        # Mostrar información del tamaño
        folder_size = self.file_service.get_folder_size(local_folder_path)
        formatted_size = self.file_service.format_size(folder_size)
        self.logger.info(f"Tamaño total a subir: {formatted_size}")

        # Subir archivos
        uploaded_count = self.gcs_service.upload_files(
            files_to_upload=files_to_upload,
            gcs_folder_name=gcs_folder_name,
            show_progress=show_progress
        )

        return uploaded_count

    def process_and_upload(self, source_path: Optional[str] = None,
                          gcs_folder_name: Optional[str] = None,
                          keep_temp: Optional[bool] = None,
                          show_progress: bool = True) -> dict:
        """
        Proceso completo: copia local y subida a GCS

        Args:
            source_path: Ruta de la carpeta origen (usa settings si es None)
            gcs_folder_name: Nombre en GCS (usa settings si es None)
            keep_temp: Si mantener la copia temporal (usa settings si es None)
            show_progress: Mostrar barra de progreso

        Returns:
            Diccionario con estadísticas del proceso:
            {
                'success': bool,
                'files_uploaded': int,
                'temp_path': str,
                'error': str (opcional)
            }
        """
        # Usar valores de settings si no se proporcionan
        source_path = source_path or self.settings.source_folder
        gcs_folder_name = gcs_folder_name or self.settings.gcs_folder_name
        keep_temp = keep_temp if keep_temp is not None else self.settings.keep_temp

        result = {
            'success': False,
            'files_uploaded': 0,
            'temp_path': None,
            'error': None
        }

        temp_path = None

        try:
            self.logger.info(f"Iniciando proceso de backup de: {source_path}")

            # Crear copia temporal
            temp_path = self.copy_folder_local(source_path)
            result['temp_path'] = temp_path

            # Subir a GCS
            files_uploaded = self.upload_folder_to_gcs(
                local_folder_path=temp_path,
                gcs_folder_name=gcs_folder_name,
                show_progress=show_progress
            )

            result['files_uploaded'] = files_uploaded
            result['success'] = files_uploaded > 0

            if result['success']:
                self.logger.info(f"Proceso completado exitosamente: {files_uploaded} archivos subidos")
            else:
                self.logger.warning("No se subieron archivos")

        except Exception as e:
            error_msg = f"Error durante el proceso: {e}"
            self.logger.error(error_msg)
            result['error'] = str(e)
            raise

        finally:
            # Limpiar copia temporal
            if temp_path and not keep_temp:
                try:
                    self.file_service.cleanup_temp(temp_path)
                except Exception as e:
                    self.logger.warning(f"No se pudo limpiar los archivos temporales: {e}")

        return result

    def verify_backup(self, gcs_folder_name: str, expected_files: int) -> bool:
        """
        Verifica que el backup se haya completado correctamente

        Args:
            gcs_folder_name: Nombre de la carpeta en GCS
            expected_files: Número esperado de archivos

        Returns:
            True si el backup es válido
        """
        try:
            uploaded_files = self.gcs_service.list_files(prefix=gcs_folder_name)
            actual_count = len(uploaded_files)

            self.logger.info(f"Verificación: {actual_count}/{expected_files} archivos")

            if actual_count == expected_files:
                self.logger.info("Backup verificado correctamente")
                return True
            else:
                self.logger.warning(f"Faltan {expected_files - actual_count} archivos en el backup")
                return False

        except Exception as e:
            self.logger.error(f"Error al verificar backup: {e}")
            return False
