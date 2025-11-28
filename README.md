# Creditoya Backup

Sistema modular y escalable para hacer backup de carpetas a Google Cloud Storage.

## 🚀 Instalación Rápida en Linux (SSH)

¿Quieres instalar en un servidor Linux? Es super simple con un solo comando:

```bash
# Clonar y ejecutar
git clone <repo-url> creditoya-backup && cd creditoya-backup && chmod +x setup.sh && ./setup.sh
```

El script interactivo te guiará por:
1. ✅ Instalación automática
2. ✅ Configuración paso a paso
3. ✅ Ejecución de backups
4. ✅ Automatización con cron
5. ✅ Ver logs y estado

📖 **[Ver guía completa de instalación en Linux →](INSTALL_LINUX.md)**

## Características

- ✅ Arquitectura modular con separación de responsabilidades
- ✅ Sistema de logging completo
- ✅ Configuración flexible (código o variables de entorno)
- ✅ Manejo de errores robusto
- ✅ Barra de progreso para operaciones largas
- ✅ Validación de configuración
- ✅ Limpieza automática de archivos temporales
- ✅ Scripts de instalación automatizada para Linux
- ✅ Configuración interactiva
- ✅ Soporte para backups automáticos con cron

## Estructura del Proyecto

```
creditoya-backup/
├── src/
│   ├── core/
│   │   └── uploader.py          # Clase principal FolderUploader
│   ├── services/
│   │   ├── file_service.py      # Operaciones de archivos locales
│   │   └── gcs_service.py       # Operaciones de Google Cloud Storage
│   ├── config/
│   │   └── settings.py          # Configuraciones
│   └── utils/
│       └── logger.py            # Sistema de logging
├── credentials/
│   └── .gitkeep                 # Coloca aquí tu archivo JSON de credenciales
├── setup.sh                     # Script TODO-EN-UNO: instalar, configurar, ejecutar (Linux)
├── main.py                      # Punto de entrada Python
├── requirements.txt             # Dependencias
├── .env.example                 # Ejemplo de variables de entorno
├── .gitignore
└── README.md                    # Guía de instalación
```

## Instalación

### Opción A: Linux/Mac (Recomendado - Automático)

Un solo script con menú interactivo para todo:

```bash
git clone <repo-url> creditoya-backup && cd creditoya-backup
chmod +x setup.sh
./setup.sh
```

El menú te permite:
- 1️⃣ Instalación inicial (automática)
- 2️⃣ Configurar sistema (interactivo)
- 3️⃣ Ejecutar backup ahora
- 4️⃣ Configurar backups automáticos (cron)
- 5️⃣ Ver logs
- 6️⃣ Verificar estado del sistema

📖 **[Ver guía detallada para Linux →](INSTALL_LINUX.md)**

### Opción B: Windows o Manual

1. Clonar el repositorio:
```bash
git clone <repo-url>
cd creditoya-backup
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar credenciales de Google Cloud:
   - Crear un proyecto en Google Cloud Console
   - Habilitar la API de Cloud Storage
   - Crear una cuenta de servicio y descargar el archivo JSON de credenciales
   - Colocar el archivo JSON en la carpeta `credentials/` (ejemplo: `credentials/mi-proyecto-gcs.json`)

## Configuración

### Opción 1: Variables de Entorno

1. Copiar el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Editar `.env` con tus valores:
```env
GCS_BUCKET_NAME=mi-bucket
GCS_CREDENTIALS_PATH=/ruta/a/credenciales.json
SOURCE_FOLDER=/u/uno
GCS_FOLDER_NAME=external_server_backup/uno_backup
```

**Nota:** Los backups se guardarán en la subcarpeta `external_server_backup/` dentro del bucket.

3. Modificar `main.py` para usar variables de entorno:
```python
# Descomentar esta línea en main.py
settings = Settings.from_env()
```

### Opción 2: Configuración Directa

Editar directamente los valores en [main.py](main.py):
```python
settings = Settings(
    bucket_name="tu-bucket-name",
    credentials_path="credentials/tu-credenciales.json",
    source_folder="/u/uno",
    gcs_folder_name="external_server_backup/uno_backup",
    keep_temp=False,
    log_level="INFO"
)
```

## Uso

### Uso Básico

```bash
python main.py
```

### Uso Programático

```python
from src.core.uploader import FolderUploader
from src.config.settings import Settings
from src.utils.logger import setup_logger

# Configurar
logger = setup_logger()
settings = Settings(
    bucket_name="mi-bucket",
    credentials_path="credenciales.json",
    source_folder="/mi/carpeta",
    gcs_folder_name="backup"
)

# Crear uploader y ejecutar
uploader = FolderUploader(settings=settings, logger=logger)
result = uploader.process_and_upload()

# Verificar resultado
if result['success']:
    print(f"Backup exitoso: {result['files_uploaded']} archivos")
else:
    print(f"Error: {result['error']}")
```

### Uso Avanzado

```python
# Solo copiar localmente
temp_path = uploader.copy_folder_local("/mi/carpeta")

# Solo subir una carpeta existente
files_uploaded = uploader.upload_folder_to_gcs(
    local_folder_path="/ruta/temp",
    gcs_folder_name="mi_backup"
)

# Verificar backup
is_valid = uploader.verify_backup("mi_backup", expected_files=100)
```

## Módulos

### Core Module (`src/core/`)
- `uploader.py`: Clase principal que orquesta todo el proceso de backup

### Services Module (`src/services/`)
- `file_service.py`: Operaciones con archivos locales (copiar, listar, limpiar)
- `gcs_service.py`: Operaciones con Google Cloud Storage (subir, listar, eliminar)

### Config Module (`src/config/`)
- `settings.py`: Gestión de configuración con validación

### Utils Module (`src/utils/`)
- `logger.py`: Sistema de logging configurable

## Logs

El sistema genera logs detallados de todas las operaciones:

```
2025-11-28 10:00:00 - creditoya_backup - INFO - Iniciando proceso de backup
2025-11-28 10:00:05 - creditoya_backup - INFO - Copiando /u/uno a /tmp/...
2025-11-28 10:00:15 - creditoya_backup - INFO - Encontrados 1500 archivos para subir
2025-11-28 10:05:30 - creditoya_backup - INFO - Subida completada: 1500/1500 archivos
```

## Manejo de Errores

El sistema maneja varios tipos de errores:

- Configuración inválida
- Archivos/carpetas no encontrados
- Errores de permisos
- Errores de conexión con GCS
- Errores durante la copia o subida

Todos los errores se registran en el log con información detallada.

## Desarrollo

### Agregar Nuevos Servicios

1. Crear un nuevo archivo en `src/services/`
2. Implementar la lógica del servicio
3. Importarlo en `src/services/__init__.py`
4. Usarlo desde `FolderUploader`

### Agregar Nuevas Configuraciones

1. Agregar el campo en `src/config/settings.py`
2. Actualizar el método `from_env()` si es necesario
3. Agregar validación en `validate()`

## Mejoras Futuras

- [ ] Soporte para múltiples proveedores de cloud (AWS S3, Azure)
- [ ] Compresión de archivos antes de subir
- [ ] Encriptación de archivos
- [ ] Reintentos automáticos en caso de fallo
- [ ] Modo incremental (solo subir archivos modificados)
- [ ] Interfaz web para monitorear backups
- [ ] Programación de backups automáticos
- [ ] Notificaciones por email/Slack

## Licencia

MIT

## Contacto

Para preguntas o sugerencias, abrir un issue en el repositorio.
