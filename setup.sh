#!/bin/bash
# Creditoya Backup - Setup y Gestión Todo-en-Uno
# Instalación, configuración y ejecución de backups

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funciones de utilidad
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
banner() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════╗
║                                               ║
║         CREDITOYA BACKUP MANAGER              ║
║     Sistema de Backup a Google Cloud          ║
║                                               ║
╚═══════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

press_enter() {
    echo ""
    read -p "Presiona ENTER para continuar..."
}

# ============================================
# FUNCIÓN 1: INSTALACIÓN INICIAL
# ============================================
install_system() {
    clear
    banner
    echo -e "${BLUE}═══ INSTALACIÓN INICIAL ═══${NC}"
    echo ""

    # Verificar Python 3
    info "Verificando Python 3..."
    if ! command -v python3 &> /dev/null; then
        error "Python 3 no está instalado."
        echo "Instálalo con:"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    info "Python encontrado: $PYTHON_VERSION"

    # Verificar pip
    info "Verificando pip..."
    if ! command -v pip3 &> /dev/null; then
        warn "pip3 no encontrado, intentando instalar..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip
        fi
    fi

    # Crear entorno virtual
    info "Creando entorno virtual..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        info "Entorno virtual creado"
    else
        info "Entorno virtual ya existe"
    fi

    # Instalar dependencias
    info "Instalando dependencias..."
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt

    # Crear directorios
    info "Creando directorios..."
    mkdir -p credentials logs

    # Crear .env si no existe
    if [ ! -f ".env" ]; then
        info "Creando archivo .env desde plantilla..."
        cp .env.example .env
    fi

    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ Instalación completada exitosamente       ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
    echo ""
    warn "SIGUIENTE PASO: Ejecuta la configuración (opción 2 del menú)"
    press_enter
}

# ============================================
# FUNCIÓN 2: CONFIGURACIÓN INTERACTIVA
# ============================================
configure_system() {
    clear
    banner
    echo -e "${BLUE}═══ CONFIGURACIÓN INTERACTIVA ═══${NC}"
    echo ""

    # Cargar valores existentes
    if [ -f ".env" ]; then
        set -a
        source .env 2>/dev/null || true
        set +a
        info "Valores actuales cargados como predeterminados"
        echo ""
    fi

    # Función auxiliar para lectura
    read_with_default() {
        local prompt="$1"
        local default="$2"
        local value
        if [ -n "$default" ]; then
            read -p "$prompt [$default]: " value
            echo "${value:-$default}"
        else
            read -p "$prompt: " value
            echo "$value"
        fi
    }

    # Recopilar configuración
    echo -e "${CYAN}Google Cloud Storage:${NC}"
    BUCKET_NAME=$(read_with_default "Nombre del bucket GCS" "$GCS_BUCKET_NAME")

    echo ""
    echo -e "${CYAN}Credenciales:${NC}"
    echo "Archivos JSON disponibles en credentials/:"
    ls -1 credentials/*.json 2>/dev/null | sed 's|credentials/||' || echo "(ninguno encontrado)"
    echo ""
    CREDENTIALS=$(read_with_default "Nombre del archivo de credenciales" "$(basename ${GCS_CREDENTIALS_PATH:-mi-credenciales.json} 2>/dev/null)")

    echo ""
    echo -e "${CYAN}Configuración de carpetas:${NC}"
    SOURCE=$(read_with_default "Carpeta origen para backup" "${SOURCE_FOLDER:-/u/uno}")
    DEST=$(read_with_default "Carpeta destino en GCS" "${GCS_FOLDER_NAME:-external_server_backup/uno_backup}")

    echo ""
    echo -e "${CYAN}Opciones adicionales:${NC}"
    KEEP_TEMP_INPUT=$(read_with_default "Mantener archivos temporales? (true/false)" "${KEEP_TEMP:-false}")
    LOG_LEVEL=$(read_with_default "Nivel de logging (DEBUG/INFO/WARNING/ERROR)" "${LOG_LEVEL:-INFO}")
    LOG_FILE=$(read_with_default "Archivo de log" "${LOG_FILE:-logs/backup.log}")

    # Guardar configuración
    echo ""
    info "Guardando configuración en .env..."

    cat > .env << EOF
# Configuración de Google Cloud Storage
GCS_BUCKET_NAME=$BUCKET_NAME
GCS_CREDENTIALS_PATH=credentials/$CREDENTIALS

# Configuración de carpetas
SOURCE_FOLDER=$SOURCE
GCS_FOLDER_NAME=$DEST

# Opciones
KEEP_TEMP=$KEEP_TEMP_INPUT
LOG_LEVEL=$LOG_LEVEL
LOG_FILE=$LOG_FILE
EOF

    echo ""
    echo -e "${GREEN}✓ Configuración guardada exitosamente${NC}"
    echo ""

    # Validaciones
    if [ ! -f "credentials/$CREDENTIALS" ]; then
        warn "El archivo de credenciales no existe: credentials/$CREDENTIALS"
        echo "Cópialo usando:"
        echo "  scp tu-archivo.json usuario@servidor:$SCRIPT_DIR/credentials/$CREDENTIALS"
        echo ""
    fi

    if [ ! -d "$SOURCE" ]; then
        warn "La carpeta origen no existe: $SOURCE"
        echo ""
    fi

    press_enter
}

# ============================================
# FUNCIÓN 3: EJECUTAR BACKUP
# ============================================
run_backup() {
    clear
    banner
    echo -e "${BLUE}═══ EJECUTAR BACKUP ═══${NC}"
    echo ""

    # Cargar variables
    set -a
    source .env
    set +a

    echo -e "${CYAN}Configuración actual:${NC}"
    echo "  Bucket:         $GCS_BUCKET_NAME"
    echo "  Carpeta origen: $SOURCE_FOLDER"
    echo "  Carpeta GCS:    $GCS_FOLDER_NAME"
    echo ""

    read -p "¿Continuar con el backup? (s/n): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Ss]$ ]]; then
        warn "Backup cancelado"
        press_enter
        return
    fi

    echo ""
    echo -e "${GREEN}Iniciando backup...${NC}"
    echo ""

    # Activar entorno y ejecutar
    source venv/bin/activate
    python3 main.py

    EXIT_CODE=$?

    echo ""
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  ✓ Backup completado exitosamente            ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
    else
        echo -e "${RED}╔═══════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║  ✗ Backup falló con errores                  ║${NC}"
        echo -e "${RED}╚═══════════════════════════════════════════════╝${NC}"
        echo "Revisa los logs para más detalles: logs/backup.log"
    fi

    press_enter
    return $EXIT_CODE
}

# ============================================
# FUNCIÓN 4: CONFIGURAR BACKUPS AUTOMÁTICOS
# ============================================
setup_cron() {
    clear
    banner
    echo -e "${BLUE}═══ CONFIGURAR BACKUPS AUTOMÁTICOS (CRON) ═══${NC}"
    echo ""

    echo "Selecciona la frecuencia de los backups:"
    echo ""
    echo "  1) Diario (todos los días a las 2:00 AM)"
    echo "  2) Cada 12 horas (2:00 AM y 2:00 PM)"
    echo "  3) Cada 6 horas"
    echo "  4) Cada hora"
    echo "  5) Personalizado"
    echo "  6) Ver cron jobs actuales"
    echo "  7) Eliminar cron job"
    echo "  0) Volver"
    echo ""

    read -p "Opción [0-7]: " CRON_OPTION

    case $CRON_OPTION in
        1)
            CRON_SCHEDULE="0 2 * * *"
            DESCRIPTION="diario a las 2:00 AM"
            ;;
        2)
            CRON_SCHEDULE="0 2,14 * * *"
            DESCRIPTION="cada 12 horas (2:00 AM y 2:00 PM)"
            ;;
        3)
            CRON_SCHEDULE="0 */6 * * *"
            DESCRIPTION="cada 6 horas"
            ;;
        4)
            CRON_SCHEDULE="0 * * * *"
            DESCRIPTION="cada hora"
            ;;
        5)
            echo ""
            echo "Ingresa la expresión cron (ej: '0 3 * * *' para las 3:00 AM):"
            read -p "Expresión: " CRON_SCHEDULE
            DESCRIPTION="personalizado: $CRON_SCHEDULE"
            ;;
        6)
            echo ""
            echo "Cron jobs actuales:"
            crontab -l 2>/dev/null || echo "(ninguno)"
            press_enter
            return
            ;;
        7)
            echo ""
            crontab -l 2>/dev/null | grep -v "$SCRIPT_DIR/setup.sh" | crontab - || true
            info "Cron jobs de Creditoya Backup eliminados"
            press_enter
            return
            ;;
        0)
            return
            ;;
        *)
            error "Opción inválida"
            press_enter
            return
            ;;
    esac

    # Crear entrada de cron
    CRON_CMD="cd $SCRIPT_DIR && ./setup.sh --backup >> logs/cron_backup.log 2>&1"
    CRON_ENTRY="$CRON_SCHEDULE $CRON_CMD"

    # Backup y actualizar crontab
    crontab -l > /tmp/current_crontab 2>/dev/null || true

    if grep -q "$SCRIPT_DIR/setup.sh" /tmp/current_crontab 2>/dev/null; then
        grep -v "$SCRIPT_DIR/setup.sh" /tmp/current_crontab > /tmp/new_crontab
        echo "$CRON_ENTRY" >> /tmp/new_crontab
        crontab /tmp/new_crontab
        info "Cron job actualizado"
    else
        echo "$CRON_ENTRY" >> /tmp/current_crontab
        crontab /tmp/current_crontab
        info "Cron job agregado"
    fi

    rm -f /tmp/current_crontab /tmp/new_crontab

    echo ""
    echo -e "${GREEN}✓ Backup automático configurado${NC}"
    echo "  Frecuencia: $DESCRIPTION"
    echo "  Logs: logs/cron_backup.log"
    echo ""
    press_enter
}

# ============================================
# FUNCIÓN 5: VER LOGS
# ============================================
view_logs() {
    clear
    banner
    echo -e "${BLUE}═══ VER LOGS ═══${NC}"
    echo ""

    echo "1) Últimas 50 líneas del log principal"
    echo "2) Últimas 50 líneas del log de cron"
    echo "3) Seguir log en tiempo real (Ctrl+C para salir)"
    echo "0) Volver"
    echo ""

    read -p "Opción [0-3]: " LOG_OPTION

    case $LOG_OPTION in
        1)
            if [ -f "logs/backup.log" ]; then
                echo ""
                tail -50 logs/backup.log
            else
                warn "No hay logs disponibles"
            fi
            ;;
        2)
            if [ -f "logs/cron_backup.log" ]; then
                echo ""
                tail -50 logs/cron_backup.log
            else
                warn "No hay logs de cron disponibles"
            fi
            ;;
        3)
            if [ -f "logs/backup.log" ]; then
                echo ""
                info "Siguiendo logs en tiempo real (Ctrl+C para salir)..."
                echo ""
                tail -f logs/backup.log
            else
                warn "No hay logs disponibles"
            fi
            ;;
        0)
            return
            ;;
    esac

    echo ""
    press_enter
}

# ============================================
# FUNCIÓN 6: VERIFICAR ESTADO
# ============================================
check_status() {
    clear
    banner
    echo -e "${BLUE}═══ ESTADO DEL SISTEMA ═══${NC}"
    echo ""

    echo -e "${CYAN}Instalación:${NC}"
    if [ -d "venv" ]; then
        echo "  ✓ Entorno virtual: OK"
    else
        echo "  ✗ Entorno virtual: NO INSTALADO"
    fi

    if [ -d "credentials" ]; then
        CRED_COUNT=$(ls -1 credentials/*.json 2>/dev/null | wc -l)
        echo "  ✓ Carpeta credentials: OK ($CRED_COUNT archivos JSON)"
    else
        echo "  ✗ Carpeta credentials: NO EXISTE"
    fi

    echo ""
    echo -e "${CYAN}Configuración:${NC}"
    if [ -f ".env" ]; then
        echo "  ✓ Archivo .env: OK"
        source .env 2>/dev/null || true
        echo "    - Bucket: ${GCS_BUCKET_NAME:-NO CONFIGURADO}"
        echo "    - Origen: ${SOURCE_FOLDER:-NO CONFIGURADO}"

        if [ -f "$GCS_CREDENTIALS_PATH" ]; then
            echo "    - Credenciales: ✓ $(basename $GCS_CREDENTIALS_PATH)"
        else
            echo "    - Credenciales: ✗ NO ENCONTRADO"
        fi
    else
        echo "  ✗ Archivo .env: NO CONFIGURADO"
    fi

    echo ""
    echo -e "${CYAN}Logs:${NC}"
    if [ -f "logs/backup.log" ]; then
        LAST_BACKUP=$(tail -1 logs/backup.log 2>/dev/null || echo "Nunca")
        echo "  ✓ Log principal: OK"
        echo "    Última línea: $LAST_BACKUP"
    else
        echo "  - Log principal: Sin registros"
    fi

    echo ""
    echo -e "${CYAN}Cron Jobs:${NC}"
    if crontab -l 2>/dev/null | grep -q "$SCRIPT_DIR"; then
        echo "  ✓ Backup automático: CONFIGURADO"
        crontab -l 2>/dev/null | grep "$SCRIPT_DIR"
    else
        echo "  - Backup automático: NO CONFIGURADO"
    fi

    echo ""
    press_enter
}

# ============================================
# VERIFICAR ESTADO Y AUTO-SETUP
# ============================================
auto_setup() {
    local needs_install=false
    local needs_config=false

    # Verificar instalación
    if [ ! -d "venv" ] || [ ! -d "credentials" ] || [ ! -d "logs" ]; then
        needs_install=true
    fi

    # Verificar configuración
    if [ ! -f ".env" ]; then
        needs_config=true
    else
        source .env 2>/dev/null || needs_config=true
        if [ -z "$GCS_BUCKET_NAME" ] || [ -z "$SOURCE_FOLDER" ]; then
            needs_config=true
        fi
    fi

    # Auto-instalación si es necesario
    if [ "$needs_install" = true ]; then
        clear
        banner
        echo -e "${YELLOW}⚠ Primera ejecución detectada${NC}"
        echo ""
        info "Instalando sistema automáticamente..."
        echo ""
        sleep 1

        install_system
    fi

    # Auto-configuración si es necesario
    if [ "$needs_config" = true ]; then
        clear
        banner
        echo -e "${YELLOW}⚠ Sistema no configurado${NC}"
        echo ""
        info "Iniciando configuración interactiva..."
        echo ""
        sleep 1

        configure_system
    fi
}

# ============================================
# MENÚ PRINCIPAL
# ============================================
show_menu() {
    clear
    banner

    echo -e "${YELLOW}¿Qué deseas hacer?${NC}"
    echo ""
    echo "  1) Ejecutar backup ahora"
    echo "  2) Configurar backups automáticos (cron)"
    echo "  3) Ver logs"
    echo "  4) Verificar estado del sistema"
    echo "  5) Reconfigurar sistema"
    echo ""
    echo "  0) Salir"
    echo ""
    read -p "Selecciona una opción [0-5]: " OPTION

    case $OPTION in
        1) run_backup ;;
        2) setup_cron ;;
        3) view_logs ;;
        4) check_status ;;
        5) configure_system ;;
        0)
            clear
            echo ""
            echo -e "${GREEN}¡Hasta luego!${NC}"
            echo ""
            exit 0
            ;;
        *)
            error "Opción inválida"
            press_enter
            ;;
    esac
}

# ============================================
# MAIN
# ============================================

# Permitir ejecución directa del backup desde cron
if [ "$1" = "--backup" ]; then
    source venv/bin/activate
    set -a
    source .env
    set +a
    echo "======================================"
    echo "Backup iniciado: $(date)"
    echo "======================================"
    python3 main.py
    EXIT_CODE=$?
    echo "Backup finalizado: $(date)"
    echo "Código de salida: $EXIT_CODE"
    echo ""
    exit $EXIT_CODE
fi

# Auto-setup: verificar e instalar/configurar si es necesario
auto_setup

# Menú interactivo
while true; do
    show_menu
done
