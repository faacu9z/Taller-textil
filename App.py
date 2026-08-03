import sqlite3
import os

DB_NAME = "database.db"

def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def inicializar_base_datos():
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Tabla principal de pedidos (datos del cliente, estado y total global)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            telefono_cliente TEXT NOT NULL,
            fecha TEXT NOT NULL,
            estado TEXT NOT NULL, -- 'Activo' o 'Entregado'
            senia REAL DEFAULT 0,
            saldo REAL DEFAULT 0,
            total REAL DEFAULT 0
        )
    """)
    
    # Tabla de detalles (permite guardar múltiples talles, remeras y cantidades por pedido)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            prenda TEXT NOT NULL,
            talle TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE
        )
    """)

    # Tabla de gastos del taller
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concepto TEXT NOT NULL,
            categoria TEXT NOT NULL,
            cantidad INTEGER,
            precio_unitario REAL,
            total REAL NOT NULL,
            fecha TEXT NOT NULL
        )
    """)
    
    conexion.commit()
    conexion.close()

if __name__ == "__main__":
    inicializar_base_datos()
