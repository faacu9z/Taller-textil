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
