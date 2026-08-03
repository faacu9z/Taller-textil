"""
==========================================
FINANZAS (Versión Simplificada)
Gestión Taller Textil
==========================================
"""

import sqlite3
from datetime import datetime
from database import conectar


# ==========================================
# REGISTRAR GASTO
# ==========================================

def registrar_gasto(concepto, categoria, cantidad, precio_unitario, usuario=""):
    conexion = conectar()
    cursor = conexion.cursor()

    try:
        total = cantidad * precio_unitario
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        cursor.execute(
            """
            INSERT INTO gastos (concepto, categoria, cantidad, precio_unitario, total, fecha, usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (concepto.strip(), categoria.strip(), cantidad, precio_unitario, total, fecha, usuario)
        )
        conexion.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error registrando gasto: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()


# ==========================================
# OBTENER GASTOS
# ==========================================

def obtener_gastos():
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT * FROM gastos ORDER BY id DESC")
        return cursor.fetchall()
    finally:
        conexion.close()


# ==========================================
# TOTAL GASTOS
# ==========================================

def total_gastos():
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT SUM(total) FROM gastos")
        resultado = cursor.fetchone()
        return resultado[0] or 0.0
    finally:
        conexion.close()


# ==========================================
# TOTAL INGRESOS (Señas cobradas)
# ==========================================

def total_ingresos():
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        # Sumamos las señas ingresadas de los pedidos
        cursor.execute("SELECT SUM(senia) FROM pedidos")
        resultado = cursor.fetchone()
        return resultado[0] or 0.0
    finally:
        conexion.close()


# ==========================================
# DINERO PENDIENTE DE COBRO (Saldos)
# ==========================================

def dinero_pendiente():
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT SUM(saldo) FROM pedidos WHERE estado = 'Activo'")
        resultado = cursor.fetchone()
        return resultado[0] or 0.0
    finally:
        conexion.close()


# ==========================================
# RESUMEN FINANCIERO
# ==========================================

def resumen_financiero():
    ingresos = total_ingresos()
    gastos = total_gastos()
    pendiente = dinero_pendiente()

    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "balance": ingresos - gastos,
        "pendiente_cobro": pendiente
    }
