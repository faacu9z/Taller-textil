"""
==========================================
CONFIGURACIÓN GENERAL DEL SISTEMA
Gestión Taller Textil
==========================================
"""

from pathlib import Path
import configparser
import os

# ==========================================
# NOMBRE DEL SISTEMA
# ==========================================

APP_NAME = "Gestión Taller Textil"

VERSION = "2.0"

# ==========================================
# CONFIG.INI
# ==========================================

CONFIG_FILE = "config.ini"

config = configparser.ConfigParser(interpolation=None)

# ==========================================
# SI NO EXISTE EL CONFIG.INI LO CREA
# ==========================================

if not os.path.exists(CONFIG_FILE):

    config["RUTA"] = {
        "Servidor": str(Path.home() / "TallerTextil")
    }

    config["BASE_DE_DATOS"] = {
        "Nombre": "database.db",
        "ModoWAL": "True",
        "BusyTimeout": "5000"
    }

    config["BACKUP"] = {
        "Automatico": "True",
        "CadaMinutos": "30",
        "CadaCambios": "100"
    }

    config["GENERAL"] = {
        "Moneda": "ARS",
        "FormatoFecha": "%d/%m/%Y"
    }

    with open(CONFIG_FILE, "w", encoding="utf-8") as archivo:
        config.write(archivo)

config.read(CONFIG_FILE, encoding="utf-8")

# ==========================================
# CARPETA PRINCIPAL
# ==========================================

BASE_DIR = Path(config["RUTA"]["Servidor"])

BASE_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# SUBCARPETAS
# ==========================================

DATABASE = BASE_DIR / config["BASE_DE_DATOS"]["Nombre"]

IMAGE_DIR = BASE_DIR / "Imagenes"

EXPORT_DIR = BASE_DIR / "Exportaciones"

BACKUP_DIR = BASE_DIR / "Backups"

LOG_DIR = BASE_DIR / "Logs"

TEMP_DIR = BASE_DIR / "Temp"

ICON_DIR = BASE_DIR / "Iconos"

for carpeta in [
    IMAGE_DIR,
    EXPORT_DIR,
    BACKUP_DIR,
    LOG_DIR,
    TEMP_DIR,
    ICON_DIR
]:
    carpeta.mkdir(parents=True, exist_ok=True)

# ==========================================
# OPCIONES
# ==========================================

MODO_WAL = config.getboolean("BASE_DE_DATOS", "ModoWAL")

BUSY_TIMEOUT = config.getint("BASE_DE_DATOS", "BusyTimeout")

BACKUP_MINUTOS = config.getint("BACKUP", "CadaMinutos")

BACKUP_CAMBIOS = config.getint("BACKUP", "CadaCambios")

FORMATO_FECHA = config["GENERAL"]["FormatoFecha"]

MONEDA = config["GENERAL"]["Moneda"]

# ==========================================
# ESTADOS
# ==========================================

ESTADOS = [
    "Ingresado",
    "Diseño",
    "Esperando aprobación",
    "Impresión",
    "Plancha",
    "Costura",
    "Control de calidad",
    "Listo",
    "Entregado",
    "Cancelado"
]

# ==========================================

PRIORIDADES = [
    "Normal",
    "Alta",
    "Urgente"
]

# ==========================================

MEDIOS_PAGO = [
    "Efectivo",
    "Transferencia",
    "QR",
    "Tarjeta"
]
