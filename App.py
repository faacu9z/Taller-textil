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
import hashlib
from datetime import datetime

from database import conectar


# ==========================================
# ENCRIPTAR CONTRASEÑA
# ==========================================

def hash_password(password: str):

    return hashlib.sha256(password.encode()).hexdigest()


# ==========================================
# CREAR ADMINISTRADOR
# ==========================================

def crear_admin():

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute(

        "SELECT * FROM usuarios WHERE usuario=?",

        ("admin",)

    )

    existe = cursor.fetchone()

    if existe is None:

        cursor.execute(

            """

            INSERT INTO usuarios

            (usuario,password,fecha_creacion)

            VALUES (?,?,?)

            """,

            (

                "admin",

                hash_password("1234"),

                datetime.now().strftime("%d/%m/%Y %H:%M")

            )

        )

        conn.commit()

    conn.close()


# ==========================================
# REGISTRAR USUARIO
# ==========================================

def registrar_usuario(usuario,password):

    conn = conectar()

    cursor = conn.cursor()

    try:

        cursor.execute(

            """

            INSERT INTO usuarios

            (usuario,password,fecha_creacion)

            VALUES (?,?,?)

            """,

            (

                usuario,

                hash_password(password),

                datetime.now().strftime("%d/%m/%Y %H:%M")

            )

        )

        conn.commit()

        return True

    except:

        return False

    finally:

        conn.close()


# ==========================================
# LOGIN
# ==========================================

def login(usuario,password):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT *

        FROM usuarios

        WHERE usuario=?

        AND password=?

        """,

        (

            usuario,

            hash_password(password)

        )

    )

    datos = cursor.fetchone()

    conn.close()

    return datos


# ==========================================
# OBTENER USUARIOS
# ==========================================

def obtener_usuarios():

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT *

        FROM usuarios

        ORDER BY usuario

        """

    )

    datos = cursor.fetchall()

    conn.close()

    return datos


# ==========================================
# ELIMINAR USUARIO
# ==========================================

def eliminar_usuario(id_usuario):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute(

        "DELETE FROM usuarios WHERE id=?",

        (id_usuario,)

    )

    conn.commit()

    conn.close()
    from datetime import datetime

from database import conectar


# ==========================================
# CREAR CLIENTE
# ==========================================

def crear_cliente(

    nombre,

    telefono="",

    direccion="",

    observaciones=""

):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute(

        """

        INSERT INTO clientes

        (

        nombre,

        telefono,

        direccion,

        observaciones,

        fecha_alta

        )

        VALUES

        (?,?,?,?,?)

        """,

        (

            nombre,

            telefono,

            direccion,

            observaciones,

            datetime.now().strftime("%d/%m/%Y")

        )

    )

    conn.commit()

    conn.close()


# ==========================================
# BUSCAR CLIENTE
# ==========================================

def buscar_cliente(texto):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT *

        FROM clientes

        WHERE

        nombre LIKE ?

        OR telefono LIKE ?

        ORDER BY nombre

        """,

        (

            f"%{texto}%",

            f"%{texto}%"

        )

    )

    datos = cursor.fetchall()

    conn.close()

    return datos


# ==========================================
# TODOS LOS CLIENTES
# ==========================================

def obtener_clientes():

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT *

        FROM clientes

        ORDER BY nombre

        """

    )

    datos = cursor.fetchall()

    conn.close()

    return datos


# ==========================================
# OBTENER CLIENTE
# ==========================================

def obtener_cliente(id_cliente):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT *

        FROM clientes

        WHERE id=?

        """,

        (id_cliente,)

    )

    dato = cursor.fetchone()

    conn.close()

    return dato


# ==========================================
# EDITAR CLIENTE
# ==========================================

def editar_cliente(

    id_cliente,

    nombre,

    telefono,

    direccion,

    observaciones

):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute(

        """

        UPDATE clientes

        SET

        nombre=?,

        telefono=?,

        direccion=?,

        observaciones=?

        WHERE id=?

        """,

        (

            nombre,

            telefono,

            direccion,

            observaciones,

            id_cliente

        )

    )

    conn.commit()

    conn.close()


# ==========================================
# ELIMINAR CLIENTE
# ==========================================

def eliminar_cliente(id_cliente):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute(

        "DELETE FROM clientes WHERE id=?",

        (id_cliente,)

    )

    conn.commit()

    conn.close()
