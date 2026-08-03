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
