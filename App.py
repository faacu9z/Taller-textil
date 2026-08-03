from pathlib import Path

# ==========================================
# CONFIGURACIÓN GENERAL DEL SISTEMA
# ==========================================

APP_NAME = "Gestión Taller Textil"

VERSION = "1.0.0"

# ------------------------------------------
# Carpetas
# ------------------------------------------

BASE_DIR = Path.home() / "TallerTextil"

BASE_DIR.mkdir(exist_ok=True)

DATABASE = BASE_DIR / "taller.db"

BACKUP_DIR = BASE_DIR / "backups"

BACKUP_DIR.mkdir(exist_ok=True)

EXPORT_DIR = BASE_DIR / "exportaciones"

EXPORT_DIR.mkdir(exist_ok=True)

IMAGE_DIR = BASE_DIR / "imagenes"

IMAGE_DIR.mkdir(exist_ok=True)

FILES_DIR = BASE_DIR / "archivos"

FILES_DIR.mkdir(exist_ok=True)

# ------------------------------------------
# Estados del pedido
# ------------------------------------------

ESTADOS = [

    "Ingresado",

    "Diseño",

    "Esperando aprobación",

    "Impresión",

    "Plancha",

    "Costura",

    "Control de calidad",

    "Listo",

    "Entregado"

]

# ------------------------------------------

PRIORIDADES = [

    "Normal",

    "Alta",

    "Urgente"

]

# ------------------------------------------

MEDIOS_PAGO = [

    "Efectivo",

    "Transferencia",

    "QR",

    "Tarjeta"

]
import sqlite3

from config import DATABASE

# ==========================================
# CONEXIÓN
# ==========================================

def conectar():

    conexion = sqlite3.connect(DATABASE)

    conexion.row_factory = sqlite3.Row

    return conexion


# ==========================================
# CREAR BASE
# ==========================================

def crear_base():

    conn = conectar()

    cursor = conn.cursor()

    # ===========================
    # USUARIOS
    # ===========================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS usuarios(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        usuario TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        fecha_creacion TEXT

    )

    """)

    # ===========================
    # CLIENTES
    # ===========================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS clientes(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nombre TEXT NOT NULL,

        telefono TEXT,

        direccion TEXT,

        observaciones TEXT,

        fecha_alta TEXT

    )

    """)

    # ===========================
    # PEDIDOS
    # ===========================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS pedidos(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        cliente_id INTEGER,

        prenda TEXT,

        cantidad INTEGER,

        diseño TEXT,

        archivo TEXT,

        imagen TEXT,

        tabla_talles TEXT,

        observaciones TEXT,

        estado TEXT,

        prioridad TEXT,

        vendedor TEXT,

        fecha_ingreso TEXT,

        fecha_entrega TEXT,

        fecha_real TEXT,

        precio REAL,

        pagado REAL DEFAULT 0,

        saldo REAL,

        FOREIGN KEY(cliente_id)

        REFERENCES clientes(id)

    )

    """)

    # ===========================
    # PAGOS
    # ===========================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS pagos(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        pedido_id INTEGER,

        fecha TEXT,

        monto REAL,

        medio TEXT,

        observacion TEXT,

        FOREIGN KEY(pedido_id)

        REFERENCES pedidos(id)

    )

    """)

    # ===========================
    # GASTOS
    # ===========================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS gastos(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        fecha TEXT,

        categoria TEXT,

        descripcion TEXT,

        cantidad REAL,

        precio REAL,

        total REAL

    )

    """)

    conn.commit()

    conn.close()
