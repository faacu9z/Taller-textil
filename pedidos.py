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
