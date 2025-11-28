# Paso 1: Preparar el Servidor

## Conectarte al servidor
```bash
ssh usuario@tu-servidor
```

## Actualizar sistema (Ubuntu/Debian)
```bash
sudo apt update && sudo apt upgrade -y
```

## Instalar dependencias necesarias
```bash
sudo apt install -y python3 python3-pip python3-venv git
```

## O en CentOS/RHEL
```bash
sudo yum update -y
```
```bash
sudo yum install -y python3 python3-pip git
```

# Paso 2: Clonar el Repositorio

## Ubicarte en el directorio deseado (ejemplo: home)
```bash
cd ~
```

## Clonar el repositorio
```bash
git clone https://github.com/TripKode/creditoya-backup-script.git
```

## Entrar al directorio
```bash
cd creditoya-backup-script
```

## Verificar que se clonó correctamente
```bash
ls -la
```

# Paso 3: Copiar Credenciales de Google Cloud
Desde tu computadora local, copia el archivo de credenciales JSON:

## Formato general
```bash
scp /ruta/local/tu-credenciales.json usuario@tu-servidor:~/creditoya-backup/credentials/
```

## Ejemplo real
```bash
scp ~/Downloads/mi-proyecto-gcs-123456.json root@192.168.1.100:~/creditoya-backup/credentials/
```
Verificar que se copió:

## En el servidor
```bash
ls -la ~/creditoya-backup/credentials/
```
Deberías ver tu archivo .json.

# Paso 4: Ejecutar Setup (Primera Vez)

## En el servidor
```bash
cd ~/creditoya-backup
```

## Hacer ejecutable el script
```bash
chmod +x setup.sh
```

## Ejecutar
```bash
./setup.sh
```

# Paso 5: Instalación Automática
El script detectará que es la primera vez y mostrará:
╔═══════════════════════════════════════════════╗
║                                               ║
║         CREDITOYA BACKUP MANAGER              ║
║     Sistema de Backup a Google Cloud          ║
║                                               ║
╚═══════════════════════════════════════════════╝

⚠ Primera ejecución detectada

[INFO] Instalando sistema automáticamente...
Esto instalará:
✅ Entorno virtual Python
✅ Todas las dependencias (google-cloud-storage, tqdm, etc.)
✅ Carpetas necesarias (logs, credentials)
✅ Archivo .env desde plantilla
Presiona ENTER cuando termine.

# Paso 6: Configuración Interactiva
Luego mostrará:

```bash
⚠ Sistema no configurado

[INFO] Iniciando configuración interactiva...
```
Te pedirá: 

### 1. Nombre del bucket GCS:
Nombre del bucket GCS: mi-bucket-backups

### 2. Archivo de credenciales:
Archivos JSON disponibles en credentials/:
mi-proyecto-gcs-123456.json

```bash
Nombre del archivo de credenciales [mi-credenciales.json]: mi-proyecto-gcs-123456.json
```

### 3. Carpeta origen:
Carpeta origen para backup [/u/uno]: /home/usuario/datos

### 4. Carpeta destino en GCS:
Carpeta destino en GCS [external_server_backup/uno_backup]: external_server_backup/mi_servidor

### 5. Opciones adicionales:
```bash
Mantener archivos temporales? (true/false) [false]: false
Nivel de logging (DEBUG/INFO/WARNING/ERROR) [INFO]: INFO
Archivo de log [logs/backup.log]: logs/backup.log
Presiona ENTER después de cada pregunta.
```

### Paso 7: Ver el Menú Principal
Ahora verás:
```bash
╔═══════════════════════════════════════════════╗
║                                               ║
║         CREDITOYA BACKUP MANAGER              ║
║     Sistema de Backup a Google Cloud          ║
║                                               ║
╚═══════════════════════════════════════════════╝

¿Qué deseas hacer?

  1) Ejecutar backup ahora
  2) Configurar backups automáticos (cron)
  3) Ver logs
  4) Verificar estado del sistema
  5) Reconfigurar sistema

  0) Salir

Selecciona una opción [0-5]:
```
### Paso 8: Probar el Backup (Primera Prueba)
Selecciona opción 1 para ejecutar un backup de prueba:
Selecciona una opción [0-5]: 1
Verás:

```bash
═══ EJECUTAR BACKUP ═══

Configuración actual:
  Bucket:         mi-bucket-backups
  Carpeta origen: /home/usuario/datos
  Carpeta GCS:    external_server_backup/mi_servidor

¿Continuar con el backup? (s/n): s
Escribe s y ENTER. El backup comenzará:
Iniciando backup...
Copiando /home/usuario/datos a /tmp/xyz...
Encontrados 1500 archivos para subir
Tamaño total a subir: 2.5 GB
Subiendo archivos: 100%|████████████| 1500/1500
Subida completada: 1500/1500 archivos

╔═══════════════════════════════════════════════╗
║  ✓ Backup completado exitosamente            ║
╚═══════════════════════════════════════════════╝
```

### Paso 9: Configurar Backups Automáticos (Opcional)
Si quieres backups automáticos, selecciona opción 2:
Selecciona una opción [0-5]: 2
Elige la frecuencia:

```bash
═══ CONFIGURAR BACKUPS AUTOMÁTICOS (CRON) ═══

Selecciona la frecuencia de los backups:

  1) Diario (todos los días a las 2:00 AM)
  2) Cada 12 horas (2:00 AM y 2:00 PM)
  3) Cada 6 horas
  4) Cada hora
  5) Personalizado
  6) Ver cron jobs actuales
  7) Eliminar cron job
  0) Volver

Opción [0-7]: 1
```
Ejemplo: Selecciona 1 para backup diario. 
Confirmación:
```bash
✓ Backup automático configurado
  Frecuencia: diario a las 2:00 AM
  Logs: logs/cron_backup.log
```

### Paso 10: Verificar que Todo Funciona
Selecciona opción 4 para verificar el estado:
Selecciona una opción [0-5]: 4
Verás:

```bash
═══ ESTADO DEL SISTEMA ═══

Instalación:
  ✓ Entorno virtual: OK
  ✓ Carpeta credentials: OK (1 archivos JSON)

Configuración:
  ✓ Archivo .env: OK
    - Bucket: mi-bucket-backups
    - Origen: /home/usuario/datos
    - Credenciales: ✓ mi-proyecto-gcs-123456.json

Logs:
  ✓ Log principal: OK
    Última línea: Backup completado exitosamente

Cron Jobs:
  ✓ Backup automático: CONFIGURADO
  0 2 * * * cd /root/creditoya-backup && ./setup.sh --backup >> logs/cron_backup.log 2>&1
```

### Paso 11: Salir
Selecciona opción 0 para salir:
Selecciona una opción [0-5]: 0
```bash
¡Hasta luego!
```