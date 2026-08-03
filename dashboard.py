"""
==========================================
DASHBOARD
Gestión Taller Textil
==========================================

Funciones:
- Panel principal
- Métricas generales
- Estado de producción
- Resumen financiero
"""


import streamlit as st

from pedidos import (
    estadisticas_produccion,
    pedidos_por_estado
)

from finanzas import (
    resumen_financiero
)

from config import ESTADOS



# ==========================================
# TARJETA METRICA
# ==========================================

def tarjeta(
    titulo,
    valor,
    icono=""
):
    """
    Crea una tarjeta visual
    de estadísticas.
    """

    st.markdown(
        f"""
        <div style="
            background:white;
            padding:20px;
            border-radius:12px;
            border:1px solid #ddd;
            text-align:center;
        ">

        <h3>{icono} {titulo}</h3>

        <h2>{valor}</h2>

        </div>
        """,

        unsafe_allow_html=True
    )



# ==========================================
# MOSTRAR DASHBOARD
# ==========================================

def mostrar_dashboard():

    st.title(
        "🧵 Panel de Control"
    )


    # ------------------------------
    # PRODUCCION
    # ------------------------------

    produccion = estadisticas_produccion()


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        tarjeta(
            "Pedidos Totales",
            produccion["total_pedidos"],
            "📦"
        )


    with col2:

        tarjeta(
            "Entregados",
            produccion["entregados"],
            "✅"
        )


    with col3:

        tarjeta(
            "En Producción",
            produccion["en_produccion"],
            "⚙️"
        )


    with col4:

        tarjeta(
            "Prendas",
            produccion["cantidad_prendas"],
            "👕"
        )



    st.divider()



    # ------------------------------
    # FINANZAS
    # ------------------------------

    st.subheader(
        "💰 Resumen Financiero"
    )


    finanzas = resumen_financiero()


    f1, f2, f3, f4 = st.columns(4)


    with f1:

        tarjeta(
            "Ingresos",
            f"${finanzas['ingresos']:,.0f}",
            "💵"
        )


    with f2:

        tarjeta(
            "Gastos",
            f"${finanzas['gastos']:,.0f}",
            "🛒"
        )


    with f3:

        tarjeta(
            "Balance",
            f"${finanzas['balance']:,.0f}",
            "📈"
        )


    with f4:

        tarjeta(
            "Pendiente",
            f"${finanzas['pendiente_cobro']:,.0f}",
            "⏳"
        )
        # ==========================================
# ESTADO DE PRODUCCION
# ==========================================

def mostrar_estados():

    st.subheader(
        "🏭 Producción por etapa"
    )


    columnas = st.columns(
        len(ESTADOS)
    )


    for posicion, estado in enumerate(ESTADOS):

        pedidos = pedidos_por_estado(
            estado
        )


        with columnas[posicion]:

            st.markdown(
                f"""
                <div style="
                    background:white;
                    padding:15px;
                    border-radius:10px;
                    border:1px solid #ddd;
                    text-align:center;
                ">

                <h4>{estado}</h4>

                <h2>{len(pedidos)}</h2>

                </div>
                """,

                unsafe_allow_html=True
            )



# ==========================================
# TABLA DE PRODUCCION
# ==========================================

def mostrar_tabla_produccion():

    st.subheader(
        "📋 Pedidos actuales"
    )


    produccion = estadisticas_produccion()


    if produccion["en_produccion"] == 0:

        st.info(
            "No hay pedidos en producción."
        )

        return



    for estado in ESTADOS:

        pedidos = pedidos_por_estado(
            estado
        )


        if pedidos:

            with st.expander(
                f"{estado} ({len(pedidos)})"
            ):

                for pedido in pedidos:

                    st.write(
                        f"""
                        **Pedido #{pedido[0]}**

                        Cliente ID:
                        {pedido[1]}

                        Prenda:
                        {pedido[2]}

                        Cantidad:
                        {pedido[3]}

                        """
                    )

                    st.divider()



# ==========================================
# DASHBOARD COMPLETO
# ==========================================

def dashboard_completo():

    mostrar_dashboard()

    st.divider()

    mostrar_estados()

    st.divider()

    mostrar_tabla_produccion()
