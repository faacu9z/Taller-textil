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
