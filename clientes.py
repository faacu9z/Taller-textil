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
