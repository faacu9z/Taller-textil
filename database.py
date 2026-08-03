"""
==========================================
BASE DE DATOS
Gestión Taller Textil (Versión Simplificada)
==========================================
"""

import sqlite3
from config import DATABASE, MODO_WAL, BUSY_TIMEOUT

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


def inicializar_base():
    """
    Crea todas las tablas necesarias simplificadas
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

        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nro_archivo TEXT,
            cliente_nombre TEXT NOT NULL,
            cliente_whatsapp TEXT NOT NULL,
            tomado_por TEXT,
            precio_total REAL NOT NULL DEFAULT 0,
            senia REAL NOT NULL DEFAULT 0,
            saldo REAL NOT NULL DEFAULT 0,
            observaciones TEXT,
            estado TEXT NOT NULL DEFAULT 'Activo',
            fecha_creacion TEXT
        );

        CREATE TABLE IF NOT EXISTS detalle_pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            nombre_apodo TEXT,
            talle TEXT,
            numero TEXT,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS imagenes_pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            ruta_imagen TEXT,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
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
        """
    )

    conexion.commit()
    conexion.close()

# Se ejecuta al importar el módulo
inicializar_base()
