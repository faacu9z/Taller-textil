"""
==========================================
GESTIÓN DE PEDIDOS (Versión Simplificada)
Gestión Taller Textil
==========================================

Funciones:
- Crear pedidos (Nombre, WhatsApp, Nro Archivo, Seña, Saldo)
- Detalle de prendas (Nombre/Apodo, Talle, Número)
- Gestión de imágenes y enlaces a WhatsApp
- Cancelar / Eliminar pedidos
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

from database import conectar
from config import IMAGE_DIR


# ==========================================
# GENERAR NOMBRE ÚNICO DE IMAGEN
# ==========================================

def generar_nombre_imagen(extension):
    fecha = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"{fecha}{extension}"


# ==========================================
# GUARDAR IMAGEN DEL PEDIDO
# ==========================================

def guardar_imagen(archivo):
    """
    Copia una imagen al servidor y devuelve su nombre único.
    """
    if archivo is None:
        return None

    extension = Path(archivo.name).suffix.lower()
    extensiones_validas = [".png", ".jpg", ".jpeg", ".webp"]

    if extension not in extensiones_validas:
        return None

    nombre = generar_nombre_imagen(extension)
    destino = IMAGE_DIR / nombre

    with open(destino, "wb") as salida:
        shutil.copyfileobj(archivo, salida)

    return nombre


# ==========================================
# CREAR PEDIDO
# ==========================================

def crear_pedido(
    nro_archivo,
    cliente_nombre,
    cliente_whatsapp,
    tomado_por,
    precio_total,
    senia,
    observaciones,
    prendas,        # Lista de tuplas/diccionarios: [(nombre_apodo, talle, numero), ...]
    imagenes        # Lista de rutas de archivos de imágenes seleccionadas
):
    """
    Crea un nuevo pedido con sus prendas y múltiples imágenes opcionales.
    Calcula el saldo automáticamente (Precio Total - Seña).
    """
    if not cliente_nombre or not cliente_whatsapp:
        return None

    saldo = precio_total - senia
    fecha_creacion = datetime.now().strftime("%d/%m/%Y %H:%M")

    conexion = conectar()
    cursor = conexion.cursor()

    try:
        # 1. Insertar cabecera del pedido
        cursor.execute(
            """
            INSERT INTO pedidos
            (
                nro_archivo,
                cliente_nombre,
                cliente_whatsapp,
                tomado_por,
                precio_total,
                senia,
                saldo,
                observaciones,
                estado,
                fecha_creacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Activo', ?)
            """,
            (
                nro_archivo.strip() if nro_archivo else "",
                cliente_nombre.strip(),
                cliente_whatsapp.strip(),
                tomado_por.strip() if tomado_por else "",
                precio_total,
                senia,
                saldo,
                observaciones.strip() if observaciones else "",
                fecha_creacion
            )
        )

        pedido_id = cursor.lastrowid

        # 2. Insertar detalle de prendas (Tabla de nombres, talles y números)
        if prendas:
            for p in prendas:
                # p puede ser un diccionario o tupla (nombre_apodo, talle, numero)
                cursor.execute(
                    """
                    INSERT INTO detalle_pedidos (pedido_id, nombre_apodo, talle, numero)
                    VALUES (?, ?, ?, ?)
                    """,
                    (pedido_id, p.get("nombre", ""), p.get("talle", ""), p.get("numero", ""))
                )

        # 3. Guardar e insertar imágenes asociadas
        if imagenes:
            for img in imagenes:
                nombre_img = guardar_imagen(img)
                if nombre_img:
                    cursor.execute(
                        """
                        INSERT INTO imagenes_pedidos (pedido_id, ruta_imagen)
                        VALUES (?, ?)
                        """,
                        (pedido_id, nombre_img)
                    )

        conexion.commit()
        return pedido_id

    except sqlite3.Error as e:
        print(f"Error al crear pedido: {e}")
        conexion.rollback()
        return None

    finally:
        conexion.close()


# ==========================================
# OBTENER PEDIDO COMPLETO
# ==========================================

def obtener_pedido(id_pedido):
    """
    Devuelve un diccionario o Row con los datos principales,
    más sus prendas e imágenes asociadas.
    """
    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT * FROM pedidos WHERE id = ?", (id_pedido,))
        pedido = cursor.fetchone()

        if not pedido:
            return None

        # Obtener prendas
        cursor.execute("SELECT * FROM detalle_pedidos WHERE pedido_id = ?", (id_pedido,))
        prendas = cursor.fetchall()

        # Obtener imágenes
        cursor.execute("SELECT * FROM imagenes_pedidos WHERE pedido_id = ?", (id_pedido,))
        imagenes = cursor.fetchall()

        return {
            "pedido": pedido,
            "prendas": prendas,
            "imagenes": imagenes
        }

    finally:
        conexion.close()


# ==========================================
# LISTAR PEDIDOS
# ==========================================

def obtener_pedidos(estado="Activo"):
    """
    Devuelve todos los pedidos filtrados por estado (por defecto 'Activo').
    """
    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT * FROM pedidos
            WHERE estado = ?
            ORDER BY id DESC
            """,
            (estado,)
        )
        return cursor.fetchall()

    finally:
        conexion.close()


# ==========================================
# BUSCAR PEDIDOS
# ==========================================

def buscar_pedidos(texto, estado="Activo"):
    """
    Busca pedidos por Nombre, WhatsApp, Nro de Archivo u Observaciones.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    busqueda = f"%{texto}%"

    try:
        cursor.execute(
            """
            SELECT * FROM pedidos
            WHERE estado = ? AND (
                cliente_nombre LIKE ? OR
                cliente_whatsapp LIKE ? OR
                nro_archivo LIKE ? OR
                observaciones LIKE ?
            )
            ORDER BY id DESC
            """,
            (estado, busqueda, busqueda, busqueda, busqueda)
        )
        return cursor.fetchall()

    finally:
        conexion.close()


# ==========================================
# CAMBIAR ESTADO / CANCELAR / ELIMINAR
# ==========================================

def cambiar_estado_pedido(id_pedido, nuevo_estado):
    """
    Cambia el estado del pedido (Ej: 'Activo', 'Cancelado', 'Entregado').
    """
    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            UPDATE pedidos
            SET estado = ?
            WHERE id = ?
            """,
            (nuevo_estado, id_pedido)
        )
        conexion.commit()
        return True

    except sqlite3.Error:
        conexion.rollback()
        return False

    finally:
        conexion.close()


def eliminar_pedido_definitivo(id_pedido):
    """
    Elimina físicamente el pedido y sus tablas relacionadas (Cascade).
    """
    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM pedidos WHERE id = ?", (id_pedido,))
        conexion.commit()
        return True

    except sqlite3.Error:
        conexion.rollback()
        return False

    finally:
        conexion.close()


# ==========================================
# ENLACE DIRECTO WHATSAPP
# ==========================================

def generar_link_whatsapp(telefono, mensaje=""):
    """
    Genera una URL limpia para abrir WhatsApp Web o App Directo con el número del cliente.
    """
    # Limpiar caracteres que no sean números
    tel_limpio = "".join(filter(str.isdigit, str(telefono)))
    
    # URL base de WhatsApp API
    url = f"https://wa.me/{tel_limpio}"
    if mensaje:
        import urllib.parse
        url += f"?text={urllib.parse.quote(mensaje)}"
        
    return url
