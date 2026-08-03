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
