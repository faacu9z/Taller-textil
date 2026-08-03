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
"""
==========================================
BASE DE DATOS
Gestión Taller Textil
==========================================

Funciones:
- Conectar a SQLite
- Crear tablas si no existen
"""

import sqlite3

from config import DATABASE
from config import MODO_WAL
from config import BUSY_TIMEOUT


# ==========================================
# CONECTAR
# ==========================================

def conectar():
    """
    Abre una conexión a la base de datos
    con las opciones de configuración definidas.
    """

    conexion = sqlite3.connect(
        DATABASE,
        check_same_thread=False
    )

    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()

    if MODO_WAL:
        cursor.execute("PRAGMA journal_mode=WAL")

    cursor.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT}")

    cursor.execute("PRAGMA foreign_keys=ON")

    return conexion


# ==========================================
# CREAR TABLAS (SI NO EXISTEN)
# ==========================================
#
# NOTA: esta función no existía en el proyecto
# original que se recuperó (no había ningún
# CREATE TABLE en ningún archivo), por lo que
# el esquema de abajo se construyó a partir de
# cómo se usan las columnas en el resto del
# código (auth.py, clientes.py, pedidos.py,
# finanzas.py, reportes.py). Revisar que las
# columnas coincidan con lo que necesitás.
#
# ==========================================

def inicializar_base():
    """
    Crea todas las tablas necesarias
    si todavía no existen.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fecha_creacion TEXT,
            activo INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            direccion TEXT,
            observaciones TEXT,
            fecha_creacion TEXT
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            prenda TEXT,
            cantidad INTEGER NOT NULL DEFAULT 1,
            diseno TEXT,
            imagen TEXT,
            fecha_creacion TEXT,
            estado TEXT NOT NULL DEFAULT 'Ingresado',
            prioridad TEXT NOT NULL DEFAULT 'Normal',
            precio_total REAL NOT NULL DEFAULT 0,
            total_pagado REAL NOT NULL DEFAULT 0,
            saldo REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            monto REAL NOT NULL,
            medio TEXT,
            fecha TEXT,
            usuario TEXT,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        );

        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concepto TEXT,
            categoria TEXT,
            cantidad REAL NOT NULL DEFAULT 1,
            precio_unitario REAL NOT NULL DEFAULT 0,
            total REAL NOT NULL DEFAULT 0,
            fecha TEXT,
            usuario TEXT
        );

        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            accion TEXT,
            detalle TEXT,
            fecha TEXT,
            usuario TEXT,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        );
        """
    )

    conexion.commit()

    conexion.close()


# Se ejecuta al importar el módulo para garantizar
# que las tablas existan antes de que cualquier otro
# módulo intente usarlas.
inicializar_base()
"""
==========================================
AUTENTICACIÓN
Gestión Taller Textil
==========================================

Funciones:
- Crear administrador inicial
- Registrar usuarios
- Login
- Cambiar contraseña
- Obtener usuarios
- Activar / desactivar usuarios
- Eliminar usuarios
"""

import hashlib
import sqlite3
from datetime import datetime

from database import conectar


# ==========================================
# ENCRIPTAR PASSWORD
# ==========================================

def hash_password(password: str) -> str:
    """
    Convierte una contraseña en hash SHA256.
    """

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ==========================================
# CREAR ADMINISTRADOR INICIAL
# ==========================================

def crear_admin():
    """
    Crea el usuario administrador
    si la base todavía no tiene usuarios.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT id
            FROM usuarios
            LIMIT 1
            """
        )

        usuario_existente = cursor.fetchone()

        if usuario_existente is None:

            cursor.execute(
                """
                INSERT INTO usuarios
                (
                    usuario,
                    password,
                    fecha_creacion,
                    activo
                )
                VALUES (?,?,?,1)
                """,
                (
                    "admin",
                    hash_password("1234"),
                    datetime.now().strftime(
                        "%d/%m/%Y %H:%M"
                    )
                )
            )

            conexion.commit()

            return True

        return False

    except sqlite3.Error as error:

        print(
            f"Error creando administrador: {error}"
        )

        return False

    finally:

        conexion.close()


# ==========================================
# COMPROBAR SI EXISTE USUARIO
# ==========================================

def existe_usuario(usuario: str) -> bool:
    """
    Verifica si un nombre de usuario
    ya está registrado.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT id
            FROM usuarios
            WHERE usuario=?
            """,
            (usuario,)
        )

        resultado = cursor.fetchone()

        return resultado is not None

    finally:

        conexion.close()


# ==========================================
# REGISTRAR USUARIO
# ==========================================

def registrar_usuario(
    usuario: str,
    password: str
):
    """
    Registra un nuevo usuario.
    """

    if not usuario or not password:
        return False, "Complete todos los campos"

    usuario = usuario.strip()

    if existe_usuario(usuario):
        return False, "Ese usuario ya existe"

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO usuarios
            (
                usuario,
                password,
                fecha_creacion,
                activo
            )
            VALUES (?,?,?,1)
            """,
            (
                usuario,
                hash_password(password),
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                )
            )
        )

        conexion.commit()

        return True, "Usuario creado correctamente"

    except sqlite3.Error as error:

        conexion.rollback()

        return False, str(error)

    finally:

        conexion.close()


# ==========================================
# LOGIN
# ==========================================

def login(usuario: str, password: str):
    """
    Verifica usuario y contraseña.

    Devuelve la fila del usuario si las
    credenciales son correctas y la cuenta
    está activa, o None en caso contrario.
    """

    if not usuario or not password:
        return None

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM usuarios
            WHERE usuario=?
            AND password=?
            AND activo=1
            """,
            (
                usuario.strip(),
                hash_password(password)
            )
        )

        return cursor.fetchone()

    finally:

        conexion.close()


# ==========================================
# OBTENER USUARIO POR ID
# ==========================================

def obtener_usuario(id_usuario):
    """
    Devuelve la información de un usuario.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM usuarios
            WHERE id=?
            """,
            (id_usuario,)
        )

        return cursor.fetchone()

    finally:

        conexion.close()


# ==========================================
# OBTENER TODOS LOS USUARIOS
# ==========================================

def obtener_usuarios():
    """
    Lista todos los usuarios registrados.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM usuarios
            ORDER BY usuario ASC
            """
        )

        return cursor.fetchall()

    finally:

        conexion.close()


# ==========================================
# CAMBIAR CONTRASEÑA
# ==========================================

def cambiar_password(
    id_usuario,
    nueva_password
):
    """
    Actualiza la contraseña de un usuario.
    """

    if not nueva_password:
        return False

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            UPDATE usuarios
            SET password=?
            WHERE id=?
            """,
            (
                hash_password(
                    nueva_password
                ),
                id_usuario
            )
        )

        conexion.commit()

        return True

    except sqlite3.Error:

        return False

    finally:

        conexion.close()


# ==========================================
# ACTIVAR / DESACTIVAR USUARIO
# ==========================================

def cambiar_estado(id_usuario, activo: bool):
    """
    Activa o desactiva un usuario
    (los usuarios inactivos no pueden loguearse).
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            UPDATE usuarios
            SET activo=?
            WHERE id=?
            """,
            (
                1 if activo else 0,
                id_usuario
            )
        )

        conexion.commit()

        return True

    except sqlite3.Error:

        return False

    finally:

        conexion.close()


# ==========================================
# ELIMINAR USUARIO
# ==========================================

def eliminar_usuario(id_usuario):
    """
    Elimina un usuario definitivamente.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM usuarios
            WHERE id=?
            """,
            (id_usuario,)
        )

        conexion.commit()

        return True

    except sqlite3.Error:

        return False

    finally:

        conexion.close()
"""
==========================================
GESTIÓN DE CLIENTES
Gestión Taller Textil
==========================================

Funciones:
- Crear clientes
- Editar clientes
- Buscar clientes
- Obtener información
- Estadísticas del cliente
- Historial de pedidos
"""

import sqlite3
from datetime import datetime

from database import conectar


# ==========================================
# NORMALIZAR TELEFONO
# ==========================================

def normalizar_telefono(telefono: str) -> str:
    """
    Elimina espacios, símbolos y letras
    dejando solamente números.
    """

    if not telefono:
        return ""

    return "".join(
        filtro for filtro in telefono
        if filtro.isdigit()
    )


# ==========================================
# FORMATEAR TELEFONO
# ==========================================

def formatear_telefono(telefono: str) -> str:
    """
    Devuelve un teléfono legible.
    """

    if not telefono:
        return ""

    if len(telefono) >= 10:

        return (
            "+"
            + telefono[:2]
            + " "
            + telefono[2:6]
            + " "
            + telefono[6:]
        )

    return telefono


# ==========================================
# COMPROBAR EXISTENCIA
# ==========================================

def existe_cliente(
    nombre,
    telefono=""
):
    """
    Comprueba si un cliente ya existe.

    Busca por:
    - Nombre
    - Teléfono
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        if telefono:

            telefono = normalizar_telefono(
                telefono
            )

            cursor.execute(
                """
                SELECT id
                FROM clientes
                WHERE telefono=?
                """,
                (telefono,)
            )

        else:

            cursor.execute(
                """
                SELECT id
                FROM clientes
                WHERE LOWER(nombre)=LOWER(?)
                """,
                (nombre.strip(),)
            )

        return cursor.fetchone() is not None

    finally:

        conexion.close()


# ==========================================
# CREAR CLIENTE
# ==========================================

def crear_cliente(
    nombre,
    telefono="",
    direccion="",
    observaciones=""
):
    """
    Registra un nuevo cliente.

    Devuelve (True, id_nuevo_cliente) si se
    creó correctamente, o (False, mensaje de
    error) en caso contrario.
    """

    if not nombre or not nombre.strip():
        return False, "El nombre es obligatorio"

    if existe_cliente(nombre, telefono):
        return False, "Ya existe un cliente con ese nombre o teléfono"

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO clientes
            (
                nombre,
                telefono,
                direccion,
                observaciones,
                fecha_creacion
            )
            VALUES (?,?,?,?,?)
            """,
            (
                nombre.strip(),
                normalizar_telefono(telefono),
                direccion.strip() if direccion else "",
                observaciones.strip() if observaciones else "",
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                )
            )
        )

        conexion.commit()

        return True, cursor.lastrowid

    except sqlite3.Error as error:

        conexion.rollback()

        return False, str(error)

    finally:

        conexion.close()


# ==========================================
# OBTENER TODOS LOS CLIENTES
# ==========================================

def obtener_clientes():
    """
    Devuelve todos los clientes registrados.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM clientes
            ORDER BY nombre ASC
            """
        )

        return cursor.fetchall()

    finally:

        conexion.close()


# ==========================================
# OBTENER UN CLIENTE POR ID
# ==========================================

def obtener_cliente(id_cliente):
    """
    Devuelve la información de un cliente.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM clientes
            WHERE id=?
            """,
            (id_cliente,)
        )

        return cursor.fetchone()

    finally:

        conexion.close()


# ==========================================
# BUSCAR CLIENTES
# ==========================================

def buscar_clientes(texto):
    """
    Busca clientes por:
    - Nombre
    - Teléfono
    """

    conexion = conectar()

    cursor = conexion.cursor()

    busqueda = f"%{texto.strip()}%"

    try:

        cursor.execute(
            """
            SELECT *
            FROM clientes
            WHERE
            nombre LIKE ?
            OR telefono LIKE ?
            ORDER BY nombre ASC
            """,
            (
                busqueda,
                busqueda
            )
        )

        return cursor.fetchall()

    finally:

        conexion.close()


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
    """
    Actualiza los datos de un cliente.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

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
                nombre.strip(),
                normalizar_telefono(
                    telefono
                ),
                direccion.strip(),
                observaciones.strip(),
                id_cliente
            )
        )

        conexion.commit()

        return True

    except sqlite3.Error:

        return False

    finally:

        conexion.close()


# ==========================================
# ELIMINAR CLIENTE
# ==========================================

def eliminar_cliente(
    id_cliente
):
    """
    Elimina un cliente.

    Recomendado usar solo si el cliente
    no tiene pedidos asociados, para no
    perder el historial de ventas.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM pedidos
            WHERE cliente_id=?
            """,
            (id_cliente,)
        )

        tiene_pedidos = cursor.fetchone()[0]

        if tiene_pedidos:
            return False

        cursor.execute(
            """
            DELETE FROM clientes
            WHERE id=?
            """,
            (id_cliente,)
        )

        conexion.commit()

        return True

    except sqlite3.Error:

        conexion.rollback()

        return False

    finally:

        conexion.close()


# ==========================================
# SALDO PENDIENTE DEL CLIENTE
# ==========================================

def saldo_pendiente(
    id_cliente
):
    """
    Calcula el total que el cliente
    todavía debe pagar.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT SUM(saldo)
            FROM pedidos
            WHERE cliente_id=?
            """,
            (id_cliente,)
        )

        resultado = cursor.fetchone()

        if resultado[0]:
            return resultado[0]

        return 0

    finally:

        conexion.close()


# ==========================================
# ULTIMO PEDIDO
# ==========================================

def ultimo_pedido(
    id_cliente
):
    """
    Devuelve el último pedido
    realizado por el cliente.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM pedidos
            WHERE cliente_id=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (id_cliente,)
        )

        return cursor.fetchone()

    finally:

        conexion.close()
"""
==========================================
GESTIÓN DE PEDIDOS
Gestión Taller Textil
==========================================

Funciones:
- Crear pedidos
- Editar pedidos
- Cambiar estados
- Buscar pedidos
- Manejar imágenes
- Historial de producción
- Control de pagos relacionado
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

from database import conectar

from config import IMAGE_DIR, ESTADOS


# ==========================================
# GENERAR ID DE IMAGEN
# ==========================================

def generar_nombre_imagen(
    extension
):
    """
    Genera un nombre único
    para guardar imágenes.
    """

    fecha = datetime.now().strftime(
        "%Y%m%d%H%M%S%f"
    )

    return f"{fecha}{extension}"


# ==========================================
# GUARDAR IMAGEN DEL PEDIDO
# ==========================================

def guardar_imagen(
    archivo
):
    """
    Copia una imagen al servidor.

    Acepta:
    PNG
    JPG
    JPEG
    WEBP
    """

    if archivo is None:
        return None

    extension = Path(
        archivo.name
    ).suffix.lower()

    extensiones_validas = [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    ]

    if extension not in extensiones_validas:
        return None

    nombre = generar_nombre_imagen(
        extension
    )

    destino = IMAGE_DIR / nombre

    with open(destino, "wb") as salida:
        shutil.copyfileobj(archivo, salida)

    return nombre


# ==========================================
# CREAR PEDIDO
# ==========================================

def crear_pedido(
    cliente_id,
    prenda,
    cantidad,
    diseno="",
    precio=0.0,
    imagen=None,
    prioridad="Normal"
):
    """
    Crea un nuevo pedido para un cliente.

    Devuelve el ID del pedido creado,
    o None si falló.
    """

    if not cliente_id or not prenda:
        return None

    nombre_imagen = guardar_imagen(imagen) if imagen else None

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO pedidos
            (
                cliente_id,
                prenda,
                cantidad,
                diseno,
                imagen,
                fecha_creacion,
                estado,
                prioridad,
                precio_total,
                total_pagado,
                saldo
            )
            VALUES (?,?,?,?,?,?,?,?,?,0,?)
            """,
            (
                cliente_id,
                prenda.strip(),
                cantidad,
                diseno.strip() if diseno else "",
                nombre_imagen,
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),
                ESTADOS[0],
                prioridad,
                precio,
                precio
            )
        )

        conexion.commit()

        return cursor.lastrowid

    except sqlite3.Error:

        conexion.rollback()

        return None

    finally:

        conexion.close()


# ==========================================
# OBTENER PEDIDO
# ==========================================

def obtener_pedido(
    id_pedido
):
    """
    Devuelve un pedido completo
    por su ID.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM pedidos
            WHERE id=?
            """,
            (id_pedido,)
        )

        return cursor.fetchone()

    finally:

        conexion.close()


# ==========================================
# LISTAR PEDIDOS
# ==========================================

def obtener_pedidos():
    """
    Devuelve todos los pedidos.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM pedidos
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()

    finally:

        conexion.close()


# ==========================================
# BUSCAR PEDIDOS
# ==========================================

def buscar_pedidos(
    texto
):
    """
    Busca pedidos por:

    - Cliente
    - Diseño
    - Prenda
    - Estado
    """

    conexion = conectar()

    cursor = conexion.cursor()

    busqueda = f"%{texto}%"

    try:

        cursor.execute(
            """
            SELECT
            pedidos.*
            FROM pedidos
            INNER JOIN clientes
            ON pedidos.cliente_id = clientes.id
            WHERE
            clientes.nombre LIKE ?
            OR pedidos.prenda LIKE ?
            OR pedidos.diseno LIKE ?
            OR pedidos.estado LIKE ?
            ORDER BY pedidos.id DESC
            """,
            (
                busqueda,
                busqueda,
                busqueda,
                busqueda
            )
        )

        return cursor.fetchall()

    finally:

        conexion.close()


# ==========================================
# CAMBIAR ESTADO DEL PEDIDO
# ==========================================

def cambiar_estado(
    id_pedido,
    nuevo_estado,
    usuario=""
):
    """
    Cambia la etapa de producción de un pedido
    y deja constancia en el historial.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            UPDATE pedidos
            SET estado=?
            WHERE id=?
            """,
            (
                nuevo_estado,
                id_pedido
            )
        )

        cursor.execute(
            """
            INSERT INTO historial
            (
                pedido_id,
                accion,
                detalle,
                fecha,
                usuario
            )
            VALUES (?,?,?,?,?)
            """,
            (
                id_pedido,
                "Cambio de estado",
                f"Nuevo estado: {nuevo_estado}",
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),
                usuario
            )
        )

        conexion.commit()

        return True

    except sqlite3.Error:

        conexion.rollback()

        return False

    finally:

        conexion.close()


# ==========================================
# ACTUALIZAR PRECIO DEL PEDIDO
# ==========================================

def actualizar_precio(
    id_pedido,
    nuevo_precio
):
    """
    Actualiza el precio total
    recalculando el saldo pendiente.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT total_pagado
            FROM pedidos
            WHERE id=?
            """,
            (id_pedido,)
        )

        pago = cursor.fetchone()

        if pago is None:
            return False

        saldo = nuevo_precio - pago[0]

        cursor.execute(
            """
            UPDATE pedidos
            SET
            precio_total=?,
            saldo=?
            WHERE id=?
            """,
            (
                nuevo_precio,
                saldo,
                id_pedido
            )
        )

        conexion.commit()

        return True

    finally:

        conexion.close()


# ==========================================
# AGREGAR PAGO
# ==========================================

def agregar_pago(
    id_pedido,
    monto,
    medio,
    usuario=""
):
    """
    Registra un pago
    asociado al pedido.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT
            precio_total,
            total_pagado
            FROM pedidos
            WHERE id=?
            """,
            (id_pedido,)
        )

        pedido = cursor.fetchone()

        if pedido is None:
            return False

        nuevo_total_pagado = pedido[1] + monto

        nuevo_saldo = pedido[0] - nuevo_total_pagado

        cursor.execute(
            """
            UPDATE pedidos
            SET
            total_pagado=?,
            saldo=?
            WHERE id=?
            """,
            (
                nuevo_total_pagado,
                nuevo_saldo,
                id_pedido
            )
        )

        cursor.execute(
            """
            INSERT INTO pagos
            (
                pedido_id,
                monto,
                medio,
                fecha,
                usuario
            )
            VALUES (?,?,?,?,?)
            """,
            (
                id_pedido,
                monto,
                medio,
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),
                usuario
            )
        )

        cursor.execute(
            """
            INSERT INTO historial
            (
                pedido_id,
                accion,
                detalle,
                fecha,
                usuario
            )
            VALUES (?,?,?,?,?)
            """,
            (
                id_pedido,
                "Pago registrado",
                f"Pago de ${monto} por {medio}",
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),
                usuario
            )
        )

        conexion.commit()

        return True

    except sqlite3.Error:

        conexion.rollback()

        return False

    finally:

        conexion.close()


# ==========================================
# ELIMINAR PEDIDO (SOFT DELETE)
# ==========================================

def eliminar_pedido(
    id_pedido,
    usuario=""
):
    """
    No elimina físicamente el pedido.

    Lo marca como eliminado para
    conservar historial.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            UPDATE pedidos
            SET estado=?
            WHERE id=?
            """,
            (
                "Cancelado",
                id_pedido
            )
        )

        cursor.execute(
            """
            INSERT INTO historial
            (
                pedido_id,
                accion,
                detalle,
                fecha,
                usuario
            )
            VALUES (?,?,?,?,?)
            """,
            (
                id_pedido,
                "Pedido cancelado",
                "Pedido enviado a papelera",
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),
                usuario
            )
        )

        conexion.commit()

        return True

    except sqlite3.Error:

        conexion.rollback()

        return False

    finally:

        conexion.close()


# ==========================================
# RESTAURAR PEDIDO
# ==========================================

def restaurar_pedido(
    id_pedido
):
    """
    Recupera un pedido cancelado.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            UPDATE pedidos
            SET estado=?
            WHERE id=?
            """,
            (
                ESTADOS[0],
                id_pedido
            )
        )

        conexion.commit()

        return True

    finally:

        conexion.close()


# ==========================================
# PEDIDOS POR ESTADO
# ==========================================

def pedidos_por_estado(
    estado
):
    """
    Devuelve pedidos filtrados
    por etapa de producción.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM pedidos
            WHERE estado=?
            ORDER BY id DESC
            """,
            (estado,)
        )

        return cursor.fetchall()

    finally:

        conexion.close()


# ==========================================
# PEDIDOS PENDIENTES DE ENTREGA
# ==========================================

def pedidos_pendientes():
    """
    Lista pedidos que todavía
    no fueron entregados.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM pedidos
            WHERE estado != ?
            ORDER BY id DESC
            """,
            (
                "Entregado",
            )
        )

        return cursor.fetchall()

    finally:

        conexion.close()


# ==========================================
# ESTADISTICAS DE PRODUCCION
# ==========================================

def estadisticas_produccion():
    """
    Resumen general del taller.
    """

    conexion = conectar()

    cursor = conexion.cursor()

    datos = {}

    try:

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM pedidos
            """
        )

        datos["total_pedidos"] = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM pedidos
            WHERE estado='Entregado'
            """
        )

        datos["entregados"] = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM pedidos
            WHERE estado!='Entregado'
            """
        )

        datos["en_produccion"] = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT SUM(cantidad)
            FROM pedidos
            """
        )

        cantidad = cursor.fetchone()[0]

        datos["cantidad_prendas"] = cantidad or 0

        return datos

    finally:

        conexion.close()
"""
==========================================
FINANZAS
Gestión Taller Textil
==========================================

Funciones:
- Registrar gastos
- Consultar ingresos
- Control de pagos
- Balance general
- Estadísticas financieras
"""


import sqlite3
from datetime import datetime

from database import conectar



# ==========================================
# REGISTRAR GASTO
# ==========================================

def registrar_gasto(
    concepto,
    categoria,
    cantidad,
    precio_unitario,
    usuario=""
):
    """
    Guarda un gasto del taller.
    """

    conexion = conectar()

    cursor = conexion.cursor()


    try:

        total = cantidad * precio_unitario


        cursor.execute(
            """
            INSERT INTO gastos

            (

            concepto,

            categoria,

            cantidad,

            precio_unitario,

            total,

            fecha,

            usuario

            )

            VALUES (?,?,?,?,?,?,?)

            """,

            (

                concepto,

                categoria,

                cantidad,

                precio_unitario,

                total,

                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),

                usuario

            )
        )


        conexion.commit()


        return True



    except sqlite3.Error:


        conexion.rollback()


        return False



    finally:

        conexion.close()



# ==========================================
# OBTENER GASTOS
# ==========================================

def obtener_gastos():
    """
    Devuelve todos los gastos registrados.
    """

    conexion = conectar()

    cursor = conexion.cursor()


    try:

        cursor.execute(
            """
            SELECT *

            FROM gastos

            ORDER BY id DESC

            """
        )


        return cursor.fetchall()



    finally:

        conexion.close()



# ==========================================
# BUSCAR GASTOS
# ==========================================

def buscar_gastos(
    texto
):
    """
    Busca gastos por concepto
    o categoría.
    """

    conexion = conectar()

    cursor = conexion.cursor()


    busqueda = f"%{texto}%"


    try:

        cursor.execute(
            """
            SELECT *

            FROM gastos

            WHERE

            concepto LIKE ?

            OR categoria LIKE ?

            ORDER BY id DESC

            """,

            (

                busqueda,

                busqueda

            )
        )


        return cursor.fetchall()



    finally:

        conexion.close()



# ==========================================
# ELIMINAR GASTO
# ==========================================

def eliminar_gasto(
    id_gasto
):
    """
    Elimina un registro de gasto.
    """

    conexion = conectar()

    cursor = conexion.cursor()


    try:

        cursor.execute(
            """
            DELETE FROM gastos

            WHERE id=?

            """,

            (id_gasto,)
        )


        conexion.commit()


        return True



    except sqlite3.Error:


        return False



    finally:

        conexion.close()
        # ==========================================
# TOTAL GASTOS
# ==========================================

def total_gastos():
    """
    Calcula el total gastado
    en el taller.
    """

    conexion = conectar()

    cursor = conexion.cursor()


    try:

        cursor.execute(
            """
            SELECT SUM(total)

            FROM gastos

            """
        )


        resultado = cursor.fetchone()


        return resultado[0] or 0



    finally:

        conexion.close()



# ==========================================
# TOTAL INGRESOS
# ==========================================

def total_ingresos():
    """
    Calcula todo el dinero cobrado
    de los pedidos.
    """

    conexion = conectar()

    cursor = conexion.cursor()


    try:

        cursor.execute(
            """
            SELECT SUM(total_pagado)

            FROM pedidos

            """
        )


        resultado = cursor.fetchone()


        return resultado[0] or 0



    finally:

        conexion.close()



# ==========================================
# DINERO PENDIENTE DE COBRO
# ==========================================

def dinero_pendiente():
    """
    Calcula cuánto dinero
    falta cobrar.
    """

    conexion = conectar()

    cursor = conexion.cursor()


    try:

        cursor.execute(
            """
            SELECT SUM(saldo)

            FROM pedidos

            """
        )


        resultado = cursor.fetchone()


        return resultado[0] or 0



    finally:

        conexion.close()



# ==========================================
# BALANCE NETO
# ==========================================

def balance_neto():
    """
    Ingresos cobrados
    menos gastos.
    """

    ingresos = total_ingresos()

    gastos = total_gastos()


    return ingresos - gastos



# ==========================================
# VENTAS POR PERIODO
# ==========================================

def ventas_por_fecha(
    fecha_inicio,
    fecha_fin
):
    """
    Obtiene ingresos entre fechas.

    Formato:
    DD/MM/YYYY
    """

    conexion = conectar()

    cursor = conexion.cursor()


    try:

        cursor.execute(
            """
            SELECT

            SUM(total_pagado)

            FROM pedidos

            WHERE fecha_creacion BETWEEN ? AND ?

            """,

            (

                fecha_inicio,

                fecha_fin

            )
        )


        resultado = cursor.fetchone()


        return resultado[0] or 0



    finally:

        conexion.close()



# ==========================================
# GASTOS POR CATEGORIA
# ==========================================

def gastos_por_categoria():
    """
    Agrupa gastos por categoría.
    """

    conexion = conectar()

    cursor = conexion.cursor()


    try:

        cursor.execute(
            """
            SELECT

            categoria,

            SUM(total)


            FROM gastos


            GROUP BY categoria


            ORDER BY SUM(total) DESC


            """
        )


        return cursor.fetchall()



    finally:

        conexion.close()
        # ==========================================
# ULTIMOS MOVIMIENTOS
# ==========================================

def ultimos_movimientos(
    limite=20
):
    """
    Devuelve los últimos movimientos
    financieros del taller.

    Combina:
    - Pagos recibidos
    - Gastos realizados
    """

    conexion = conectar()

    cursor = conexion.cursor()


    movimientos = []


    try:

        # PAGOS

        cursor.execute(
            """
            SELECT

            id,

            'INGRESO' AS tipo,

            monto,

            medio AS detalle,

            fecha


            FROM pagos


            ORDER BY id DESC


            LIMIT ?

            """,

            (limite,)
        )


        pagos = cursor.fetchall()


        for pago in pagos:

            movimientos.append(

                {

                    "id": pago[0],

                    "tipo": pago[1],

                    "monto": pago[2],

                    "detalle": pago[3],

                    "fecha": pago[4]

                }

            )



        # GASTOS

        cursor.execute(
            """
            SELECT

            id,

            'GASTO' AS tipo,

            total,

            concepto,

            fecha


            FROM gastos


            ORDER BY id DESC


            LIMIT ?

            """,

            (limite,)
        )


        gastos = cursor.fetchall()



        for gasto in gastos:

            movimientos.append(

                {

                    "id": gasto[0],

                    "tipo": gasto[1],

                    "monto": gasto[2],

                    "detalle": gasto[3],

                    "fecha": gasto[4]

                }

            )



        # Ordenar por fecha descendente

        movimientos.sort(

            key=lambda x: x["fecha"],

            reverse=True

        )


        return movimientos[:limite]



    finally:

        conexion.close()



# ==========================================
# RESUMEN FINANCIERO
# ==========================================

def resumen_financiero():
    """
    Devuelve todas las métricas
    principales para dashboard.
    """

    ingresos = total_ingresos()

    gastos = total_gastos()

    pendiente = dinero_pendiente()


    return {

        "ingresos": ingresos,

        "gastos": gastos,

        "balance": ingresos - gastos,

        "pendiente_cobro": pendiente

    }



# ==========================================
# EXPORTAR DATOS FINANCIEROS
# ==========================================

def datos_reporte_financiero():
    """
    Obtiene información completa
    para generar reportes.
    """

    conexion = conectar()

    cursor = conexion.cursor()


    try:

        cursor.execute(
            """
            SELECT *

            FROM gastos

            ORDER BY id DESC

            """
        )


        gastos = cursor.fetchall()



        cursor.execute(
            """
            SELECT *

            FROM pagos

            ORDER BY id DESC

            """
        )


        pagos = cursor.fetchall()



        return {

            "gastos": gastos,

            "pagos": pagos,

            "resumen": resumen_financiero()

        }



    finally:

        conexion.close()
"""
==========================================
DASHBOARD
Gestión Taller Textil
==========================================

Funciones:
- Panel principal
- Métricas generales
- Estado de producción
- Resumen financiero
"""


import streamlit as st

from pedidos import (
    estadisticas_produccion,
    pedidos_por_estado
)

from finanzas import (
    resumen_financiero
)

from config import ESTADOS



# ==========================================
# TARJETA METRICA
# ==========================================

def tarjeta(
    titulo,
    valor,
    icono=""
):
    """
    Crea una tarjeta visual
    de estadísticas.
    """

    st.markdown(
        f"""
        <div style="
            background:white;
            padding:20px;
            border-radius:12px;
            border:1px solid #ddd;
            text-align:center;
        ">

        <h3>{icono} {titulo}</h3>

        <h2>{valor}</h2>

        </div>
        """,

        unsafe_allow_html=True
    )



# ==========================================
# MOSTRAR DASHBOARD
# ==========================================

def mostrar_dashboard():

    st.title(
        "🧵 Panel de Control"
    )


    # ------------------------------
    # PRODUCCION
    # ------------------------------

    produccion = estadisticas_produccion()


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        tarjeta(
            "Pedidos Totales",
            produccion["total_pedidos"],
            "📦"
        )


    with col2:

        tarjeta(
            "Entregados",
            produccion["entregados"],
            "✅"
        )


    with col3:

        tarjeta(
            "En Producción",
            produccion["en_produccion"],
            "⚙️"
        )


    with col4:

        tarjeta(
            "Prendas",
            produccion["cantidad_prendas"],
            "👕"
        )



    st.divider()



    # ------------------------------
    # FINANZAS
    # ------------------------------

    st.subheader(
        "💰 Resumen Financiero"
    )


    finanzas = resumen_financiero()


    f1, f2, f3, f4 = st.columns(4)


    with f1:

        tarjeta(
            "Ingresos",
            f"${finanzas['ingresos']:,.0f}",
            "💵"
        )


    with f2:

        tarjeta(
            "Gastos",
            f"${finanzas['gastos']:,.0f}",
            "🛒"
        )


    with f3:

        tarjeta(
            "Balance",
            f"${finanzas['balance']:,.0f}",
            "📈"
        )


    with f4:

        tarjeta(
            "Pendiente",
            f"${finanzas['pendiente_cobro']:,.0f}",
            "⏳"
        )
        # ==========================================
# ESTADO DE PRODUCCION
# ==========================================

def mostrar_estados():

    st.subheader(
        "🏭 Producción por etapa"
    )


    columnas = st.columns(
        len(ESTADOS)
    )


    for posicion, estado in enumerate(ESTADOS):

        pedidos = pedidos_por_estado(
            estado
        )


        with columnas[posicion]:

            st.markdown(
                f"""
                <div style="
                    background:white;
                    padding:15px;
                    border-radius:10px;
                    border:1px solid #ddd;
                    text-align:center;
                ">

                <h4>{estado}</h4>

                <h2>{len(pedidos)}</h2>

                </div>
                """,

                unsafe_allow_html=True
            )



# ==========================================
# TABLA DE PRODUCCION
# ==========================================

def mostrar_tabla_produccion():

    st.subheader(
        "📋 Pedidos actuales"
    )


    produccion = estadisticas_produccion()


    if produccion["en_produccion"] == 0:

        st.info(
            "No hay pedidos en producción."
        )

        return



    for estado in ESTADOS:

        pedidos = pedidos_por_estado(
            estado
        )


        if pedidos:

            with st.expander(
                f"{estado} ({len(pedidos)})"
            ):

                for pedido in pedidos:

                    st.write(
                        f"""
                        **Pedido #{pedido[0]}**

                        Cliente ID:
                        {pedido[1]}

                        Prenda:
                        {pedido[2]}

                        Cantidad:
                        {pedido[3]}

                        """
                    )

                    st.divider()



# ==========================================
# DASHBOARD COMPLETO
# ==========================================

def dashboard_completo():

    mostrar_dashboard()

    st.divider()

    mostrar_estados()

    st.divider()

    mostrar_tabla_produccion()
"""
==========================================
REPORTES
Gestión Taller Textil
==========================================

Funciones:
- Generar reportes de pedidos
- Reportes financieros
- Exportar Excel
- Exportar PDF
"""


import pandas as pd
from datetime import datetime
from pathlib import Path

from database import conectar



# ==========================================
# RUTA REPORTES
# ==========================================

CARPETA_REPORTES = Path(
    "reportes"
)

CARPETA_REPORTES.mkdir(
    exist_ok=True
)



# ==========================================
# OBTENER PEDIDOS DATAFRAME
# ==========================================

def pedidos_dataframe():

    conexion = conectar()

    try:

        consulta = """

        SELECT

        pedidos.id AS ID,

        clientes.nombre AS Cliente,

        pedidos.prenda AS Prenda,

        pedidos.cantidad AS Cantidad,

        pedidos.estado AS Estado,

        pedidos.precio_total AS Precio,

        pedidos.total_pagado AS Pagado,

        pedidos.saldo AS Saldo,

        pedidos.fecha_creacion AS Fecha


        FROM pedidos


        INNER JOIN clientes

        ON pedidos.cliente_id = clientes.id


        ORDER BY pedidos.id DESC


        """


        df = pd.read_sql_query(
            consulta,
            conexion
        )


        return df



    finally:

        conexion.close()



# ==========================================
# OBTENER GASTOS DATAFRAME
# ==========================================

def gastos_dataframe():

    conexion = conectar()


    try:

        consulta = """

        SELECT

        id AS ID,

        concepto AS Concepto,

        categoria AS Categoria,

        cantidad AS Cantidad,

        precio_unitario AS Precio_Unitario,

        total AS Total,

        fecha AS Fecha


        FROM gastos


        ORDER BY id DESC


        """


        df = pd.read_sql_query(
            consulta,
            conexion
        )


        return df



    finally:

        conexion.close()



# ==========================================
# REPORTE GENERAL
# ==========================================

def reporte_general():

    pedidos = pedidos_dataframe()

    gastos = gastos_dataframe()


    return {

        "pedidos": pedidos,

        "gastos": gastos

    }



# ==========================================
# EXPORTAR PEDIDOS EXCEL
# ==========================================

def exportar_pedidos_excel():

    df = pedidos_dataframe()


    archivo = CARPETA_REPORTES / (
        "Pedidos_"
        +
        datetime.now().strftime(
            "%Y%m%d_%H%M"
        )
        +
        ".xlsx"
    )


    df.to_excel(
        archivo,
        index=False
    )


    return str(
        archivo
    )
    # ==========================================
# EXPORTAR GASTOS EXCEL
# ==========================================

def exportar_gastos_excel():

    df = gastos_dataframe()


    archivo = CARPETA_REPORTES / (
        "Gastos_"
        +
        datetime.now().strftime(
            "%Y%m%d_%H%M"
        )
        +
        ".xlsx"
    )


    df.to_excel(
        archivo,
        index=False
    )


    return str(
        archivo
    )



# ==========================================
# REPORTE FINANCIERO EXCEL
# ==========================================

def exportar_finanzas_excel():

    pedidos = pedidos_dataframe()

    gastos = gastos_dataframe()


    archivo = CARPETA_REPORTES / (
        "Finanzas_"
        +
        datetime.now().strftime(
            "%Y%m%d_%H%M"
        )
        +
        ".xlsx"
    )


    with pd.ExcelWriter(
        archivo,
        engine="openpyxl"
    ) as writer:


        pedidos.to_excel(
            writer,
            sheet_name="Pedidos",
            index=False
        )


        gastos.to_excel(
            writer,
            sheet_name="Gastos",
            index=False
        )


    return str(
        archivo
    )



# ==========================================
# RESUMEN DE PRODUCCION
# ==========================================

def resumen_produccion():

    df = pedidos_dataframe()


    if df.empty:

        return {

            "pedidos": 0,

            "prendas": 0,

            "entregados": 0

        }



    return {

        "pedidos":
            len(df),


        "prendas":
            int(
                df["Cantidad"]
                .sum()
            ),


        "entregados":
            len(
                df[
                    df["Estado"]
                    ==
                    "Entregado"
                ]
            )

    }



# ==========================================
# REPORTE CLIENTES
# ==========================================

def clientes_dataframe():

    conexion = conectar()


    try:

        consulta = """

        SELECT

        clientes.id AS ID,

        clientes.nombre AS Cliente,

        clientes.telefono AS Telefono,

        COUNT(pedidos.id)
        AS Cantidad_Pedidos,


        SUM(
        pedidos.total_pagado
        )
        AS Total_Comprado


        FROM clientes


        LEFT JOIN pedidos

        ON clientes.id =
        pedidos.cliente_id


        GROUP BY clientes.id


        ORDER BY Total_Comprado DESC


        """


        return pd.read_sql_query(
            consulta,
            conexion
        )



    finally:

        conexion.close()



# ==========================================
# EXPORTAR CLIENTES EXCEL
# ==========================================

def exportar_clientes_excel():

    df = clientes_dataframe()


    archivo = CARPETA_REPORTES / (
        "Clientes_"
        +
        datetime.now().strftime(
            "%Y%m%d_%H%M"
        )
        +
        ".xlsx"
    )


    df.to_excel(
        archivo,
        index=False
    )


    return str(
        archivo
        )
        # ==========================================
# EXPORTAR REPORTE COMPLETO
# ==========================================

def exportar_reporte_completo():

    pedidos = pedidos_dataframe()

    gastos = gastos_dataframe()

    clientes = clientes_dataframe()


    archivo = CARPETA_REPORTES / (

        "Reporte_Completo_"

        +

        datetime.now().strftime(
            "%Y%m%d_%H%M"
        )

        +

        ".xlsx"

    )


    with pd.ExcelWriter(
        archivo,
        engine="openpyxl"
    ) as writer:


        pedidos.to_excel(

            writer,

            sheet_name="Pedidos",

            index=False

        )


        gastos.to_excel(

            writer,

            sheet_name="Gastos",

            index=False

        )


        clientes.to_excel(

            writer,

            sheet_name="Clientes",

            index=False

        )


    return str(
        archivo
    )



# ==========================================
# REPORTE DE CLIENTE INDIVIDUAL
# ==========================================

def reporte_cliente(
    id_cliente
):

    conexion = conectar()


    try:

        consulta = """

        SELECT

        clientes.nombre AS Cliente,

        clientes.telefono AS Telefono,

        pedidos.id AS Pedido,

        pedidos.prenda AS Prenda,

        pedidos.cantidad AS Cantidad,

        pedidos.estado AS Estado,

        pedidos.precio_total AS Total,

        pedidos.saldo AS Saldo,

        pedidos.fecha_creacion AS Fecha


        FROM pedidos


        INNER JOIN clientes

        ON pedidos.cliente_id =
        clientes.id


        WHERE clientes.id=?


        ORDER BY pedidos.id DESC


        """


        return pd.read_sql_query(

            consulta,

            conexion,

            params=(
                id_cliente,
            )

        )



    finally:

        conexion.close()



# ==========================================
# EXPORTAR REPORTE CLIENTE
# ==========================================

def exportar_cliente_excel(
    id_cliente
):

    df = reporte_cliente(
        id_cliente
    )


    archivo = CARPETA_REPORTES / (

        "Cliente_"

        +

        str(id_cliente)

        +

        "_"

        +

        datetime.now().strftime(
            "%Y%m%d"
        )

        +

        ".xlsx"

    )


    df.to_excel(

        archivo,

        index=False

    )


    return str(
        archivo
    )



# ==========================================
# DATOS PARA GRAFICOS
# ==========================================

def ventas_por_mes():

    conexion = conectar()


    try:

        consulta = """

        SELECT

        substr(
        fecha_creacion,
        4,
        7
        )
        AS Mes,


        SUM(
        total_pagado
        )
        AS Total


        FROM pedidos


        GROUP BY Mes


        ORDER BY Mes


        """


        return pd.read_sql_query(

            consulta,

            conexion

        )



    finally:

        conexion.close()
"""
==========================================
APP PRINCIPAL
Gestión Taller Textil
==========================================

Ejecutar:

streamlit run app.py

==========================================
"""


import streamlit as st
import pandas as pd

from config import ESTADOS, PRIORIDADES


from auth import (
    login,
    registrar_usuario,
    crear_admin
)


from clientes import (
    obtener_clientes,
    crear_cliente,
    buscar_clientes
)


from pedidos import (
    crear_pedido,
    obtener_pedidos,
    buscar_pedidos,
    cambiar_estado,
    eliminar_pedido
)


from finanzas import (
    registrar_gasto,
    obtener_gastos,
    resumen_financiero
)


from dashboard import (
    dashboard_completo
)


from reportes import (
    exportar_reporte_completo
)



# ==========================================
# CONFIGURACION
# ==========================================

st.set_page_config(

    page_title="Taller Textil",

    page_icon="🧵",

    layout="wide"

)



crear_admin()



# ==========================================
# SESION
# ==========================================

if "usuario" not in st.session_state:

    st.session_state.usuario = None



# ==========================================
# LOGIN
# ==========================================

def pantalla_login():


    st.title(
        "🧵 Gestión Taller Textil"
    )


    col1, col2, col3 = st.columns(
        [1,2,1]
    )


    with col2:


        usuario = st.text_input(
            "Usuario"
        )


        password = st.text_input(
            "Contraseña",
            type="password"
        )


        if st.button(
            "Ingresar",
            use_container_width=True
        ):


            datos = login(
                usuario,
                password
            )


            if datos:


                st.session_state.usuario = usuario

                st.success(
                    "Ingreso correcto"
                )

                st.rerun()



            else:


                st.error(
                    "Usuario o contraseña incorrectos"
                )



    st.divider()


    with st.expander(
        "Registrar usuario nuevo"
    ):


        nuevo_usuario = st.text_input(
            "Nuevo usuario"
        )


        nueva_password = st.text_input(
            "Nueva contraseña",
            type="password"
        )


        if st.button(
            "Crear usuario"
        ):


            ok, mensaje = registrar_usuario(

                nuevo_usuario,

                nueva_password

            )


            if ok:

                st.success(
                    mensaje
                )

            else:

                st.error(
                    mensaje
                )



# ==========================================
# CONTROL LOGIN
# ==========================================

if st.session_state.usuario is None:

    pantalla_login()

    st.stop()
    # ==========================================
# MENU PRINCIPAL
# ==========================================

st.sidebar.title(
    "🧵 Taller Textil"
)


st.sidebar.write(
    f"Usuario: {st.session_state.usuario}"
)



if st.sidebar.button(
    "Cerrar sesión"
):

    st.session_state.usuario = None

    st.rerun()



menu = st.sidebar.radio(

    "Secciones",

    [

        "Dashboard",

        "Clientes",

        "Pedidos",

        "Finanzas",

        "Reportes"

    ]

)



# ==========================================
# DASHBOARD
# ==========================================

if menu == "Dashboard":


    dashboard_completo()



# ==========================================
# CLIENTES
# ==========================================

elif menu == "Clientes":


    st.title(
        "👥 Clientes"
    )


    busqueda = st.text_input(
        "Buscar cliente"
    )



    if busqueda:


        clientes = buscar_clientes(
            busqueda
        )


    else:


        clientes = obtener_clientes()



    st.subheader(
        "Listado"
    )


    if clientes:


        for cliente in clientes:


            with st.expander(
                f"{cliente[1]}"
            ):


                st.write(
                    f"📞 Teléfono: {cliente[2]}"
                )


                st.write(
                    f"📍 Dirección: {cliente[3]}"
                )


                st.write(
                    f"📝 Observaciones: {cliente[4]}"
                )



    else:

        st.info(
            "No hay clientes"
        )



    st.divider()



    st.subheader(
        "Nuevo cliente"
    )


    with st.form(
        "nuevo_cliente"
    ):


        nombre = st.text_input(
            "Nombre"
        )


        telefono = st.text_input(
            "Teléfono"
        )


        direccion = st.text_input(
            "Dirección"
        )


        observaciones = st.text_area(
            "Observaciones"
        )



        guardar = st.form_submit_button(
            "Guardar cliente"
        )



        if guardar:


            resultado, mensaje = crear_cliente(

                nombre,

                telefono,

                direccion,

                observaciones

            )


            if resultado:

                st.success(
                    f"Cliente creado ID {mensaje}"
                )

                st.rerun()


            else:

                st.error(
                    mensaje
                )
                # ==========================================
# PEDIDOS
# ==========================================

elif menu == "Pedidos":


    st.title(
        "📦 Pedidos"
    )


    busqueda = st.text_input(
        "Buscar pedido"
    )



    if busqueda:


        pedidos = buscar_pedidos(
            busqueda
        )


    else:


        pedidos = obtener_pedidos()



    st.subheader(
        "Pedidos registrados"
    )



    if pedidos:


        for pedido in pedidos:


            with st.expander(
                f"Pedido #{pedido[0]} - Cliente ID {pedido[1]}"
            ):


                st.write(
                    f"👕 Prenda: {pedido[2]}"
                )


                st.write(
                    f"Cantidad: {pedido[3]}"
                )


                st.write(
                    f"Estado: {pedido[7]}"
                )


                st.write(
                    f"Total: ${pedido[9]}"
                )


                st.write(
                    f"Pagado: ${pedido[10]}"
                )


                st.write(
                    f"Saldo: ${pedido[11]}"
                )



                nuevo_estado = st.selectbox(

                    "Cambiar estado",

                    ESTADOS,

                    index=ESTADOS.index(pedido[7])
                    if pedido[7] in ESTADOS else 0,

                    key=f"estado_{pedido[0]}"

                )



                if st.button(

                    "Actualizar estado",

                    key=f"actualizar_{pedido[0]}"

                ):


                    cambiar_estado(

                        pedido[0],

                        nuevo_estado,

                        st.session_state.usuario

                    )


                    st.success(
                        "Estado actualizado"
                    )


                    st.rerun()



                if st.button(

                    "Cancelar pedido",

                    key=f"eliminar_{pedido[0]}"

                ):


                    eliminar_pedido(

                        pedido[0],

                        st.session_state.usuario

                    )


                    st.warning(
                        "Pedido cancelado"
                    )


                    st.rerun()



    else:


        st.info(
            "No existen pedidos"
        )



    st.divider()



    st.subheader(
        "Crear nuevo pedido"
    )


    clientes = obtener_clientes()



    if clientes:


        opciones = {

            f"{c[1]} - {c[2]}": c[0]

            for c in clientes

        }



        cliente_nombre = st.selectbox(

            "Cliente",

            list(opciones.keys())

        )



        cliente_id = opciones[
            cliente_nombre
        ]



        with st.form(
            "nuevo_pedido"
        ):


            prenda = st.text_input(
                "Prenda"
            )


            cantidad = st.number_input(

                "Cantidad",

                min_value=1,

                value=1

            )


            diseno = st.text_input(
                "Diseño"
            )


            precio = st.number_input(

                "Precio total",

                min_value=0.0

            )


            prioridad = st.selectbox(
                "Prioridad",
                PRIORIDADES
            )


            guardar = st.form_submit_button(

                "Crear pedido"

            )



            if guardar:


                pedido = crear_pedido(

                    cliente_id,

                    prenda,

                    cantidad,

                    diseno,

                    precio,

                    prioridad=prioridad

                )


                if pedido:


                    st.success(
                        f"Pedido creado #{pedido}"
                    )


                    st.rerun()



    else:


        st.warning(
            "Primero cree un cliente"
        )
        # ==========================================
# FINANZAS
# ==========================================

elif menu == "Finanzas":


    st.title(
        "💰 Finanzas"
    )


    resumen = resumen_financiero()



    c1, c2, c3, c4 = st.columns(4)



    c1.metric(

        "Ingresos",

        f"${resumen['ingresos']:,.0f}"

    )


    c2.metric(

        "Gastos",

        f"${resumen['gastos']:,.0f}"

    )


    c3.metric(

        "Balance",

        f"${resumen['balance']:,.0f}"

    )


    c4.metric(

        "Pendiente",

        f"${resumen['pendiente_cobro']:,.0f}"

    )



    st.divider()



    st.subheader(
        "Registrar gasto"
    )



    with st.form(
        "nuevo_gasto"
    ):


        concepto = st.text_input(
            "Concepto"
        )


        categoria = st.text_input(
            "Categoría"
        )


        cantidad = st.number_input(

            "Cantidad",

            min_value=1,

            value=1

        )


        precio = st.number_input(

            "Precio unitario",

            min_value=0.0

        )



        guardar = st.form_submit_button(

            "Guardar gasto"

        )



        if guardar:


            resultado = registrar_gasto(

                concepto,

                categoria,

                cantidad,

                precio,

                st.session_state.usuario

            )


            if resultado:


                st.success(
                    "Gasto registrado"
                )


                st.rerun()



    st.divider()



    st.subheader(
        "Historial de gastos"
    )


    gastos = obtener_gastos()



    if gastos:


        for gasto in gastos:


            st.write(

                f"""

                📅 {gasto[6]}

                🛒 {gasto[1]}

                💵 ${gasto[5]}

                """

            )


            st.divider()



# ==========================================
# REPORTES
# ==========================================

elif menu == "Reportes":


    st.title(
        "📊 Reportes"
    )


    st.write(

        "Generación de reportes del taller"

    )



    if st.button(

        "Generar reporte completo Excel"

    ):


        archivo = exportar_reporte_completo()



        st.success(

            "Reporte generado correctamente"

        )


        st.write(

            archivo

        )



# ==========================================
# FINAL APP
# ==========================================

st.sidebar.divider()


st.sidebar.caption(

    "Sistema Gestión Taller Textil"

        )
