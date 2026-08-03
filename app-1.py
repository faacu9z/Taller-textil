"""
==========================================
APP PRINCIPAL
Gestión Taller Textil
==========================================

Ejecutar:

streamlit run app.py

==========================================
"""


import streamlit as st
import pandas as pd

from config import ESTADOS, PRIORIDADES


from auth import (
    login,
    registrar_usuario,
    crear_admin
)


from clientes import (
    obtener_clientes,
    crear_cliente,
    buscar_clientes
)


from pedidos import (
    crear_pedido,
    obtener_pedidos,
    buscar_pedidos,
    cambiar_estado,
    eliminar_pedido
)


from finanzas import (
    registrar_gasto,
    obtener_gastos,
    resumen_financiero
)


from dashboard import (
    dashboard_completo
)


from reportes import (
    exportar_reporte_completo
)



# ==========================================
# CONFIGURACION
# ==========================================

st.set_page_config(

    page_title="Taller Textil",

    page_icon="🧵",

    layout="wide"

)



crear_admin()



# ==========================================
# SESION
# ==========================================

if "usuario" not in st.session_state:

    st.session_state.usuario = None



# ==========================================
# LOGIN
# ==========================================

def pantalla_login():


    st.title(
        "🧵 Gestión Taller Textil"
    )


    col1, col2, col3 = st.columns(
        [1,2,1]
    )


    with col2:


        usuario = st.text_input(
            "Usuario"
        )


        password = st.text_input(
            "Contraseña",
            type="password"
        )


        if st.button(
            "Ingresar",
            use_container_width=True
        ):


            datos = login(
                usuario,
                password
            )


            if datos:


                st.session_state.usuario = usuario

                st.success(
                    "Ingreso correcto"
                )

                st.rerun()



            else:


                st.error(
                    "Usuario o contraseña incorrectos"
                )



    st.divider()


    with st.expander(
        "Registrar usuario nuevo"
    ):


        nuevo_usuario = st.text_input(
            "Nuevo usuario"
        )


        nueva_password = st.text_input(
            "Nueva contraseña",
            type="password"
        )


        if st.button(
            "Crear usuario"
        ):


            ok, mensaje = registrar_usuario(

                nuevo_usuario,

                nueva_password

            )


            if ok:

                st.success(
                    mensaje
                )

            else:

                st.error(
                    mensaje
                )



# ==========================================
# CONTROL LOGIN
# ==========================================

if st.session_state.usuario is None:

    pantalla_login()

    st.stop()
    # ==========================================
# MENU PRINCIPAL
# ==========================================

st.sidebar.title(
    "🧵 Taller Textil"
)


st.sidebar.write(
    f"Usuario: {st.session_state.usuario}"
)



if st.sidebar.button(
    "Cerrar sesión"
):

    st.session_state.usuario = None

    st.rerun()



menu = st.sidebar.radio(

    "Secciones",

    [

        "Dashboard",

        "Clientes",

        "Pedidos",

        "Finanzas",

        "Reportes"

    ]

)



# ==========================================
# DASHBOARD
# ==========================================

if menu == "Dashboard":


    dashboard_completo()



# ==========================================
# CLIENTES
# ==========================================

elif menu == "Clientes":


    st.title(
        "👥 Clientes"
    )


    busqueda = st.text_input(
        "Buscar cliente"
    )



    if busqueda:


        clientes = buscar_clientes(
            busqueda
        )


    else:


        clientes = obtener_clientes()



    st.subheader(
        "Listado"
    )


    if clientes:


        for cliente in clientes:


            with st.expander(
                f"{cliente[1]}"
            ):


                st.write(
                    f"📞 Teléfono: {cliente[2]}"
                )


                st.write(
                    f"📍 Dirección: {cliente[3]}"
                )


                st.write(
                    f"📝 Observaciones: {cliente[4]}"
                )



    else:

        st.info(
            "No hay clientes"
        )



    st.divider()



    st.subheader(
        "Nuevo cliente"
    )


    with st.form(
        "nuevo_cliente"
    ):


        nombre = st.text_input(
            "Nombre"
        )


        telefono = st.text_input(
            "Teléfono"
        )


        direccion = st.text_input(
            "Dirección"
        )


        observaciones = st.text_area(
            "Observaciones"
        )



        guardar = st.form_submit_button(
            "Guardar cliente"
        )



        if guardar:


            resultado, mensaje = crear_cliente(

                nombre,

                telefono,

                direccion,

                observaciones

            )


            if resultado:

                st.success(
                    f"Cliente creado ID {mensaje}"
                )

                st.rerun()


            else:

                st.error(
                    mensaje
                )
                # ==========================================
# PEDIDOS
# ==========================================

elif menu == "Pedidos":


    st.title(
        "📦 Pedidos"
    )


    busqueda = st.text_input(
        "Buscar pedido"
    )



    if busqueda:


        pedidos = buscar_pedidos(
            busqueda
        )


    else:


        pedidos = obtener_pedidos()



    st.subheader(
        "Pedidos registrados"
    )



    if pedidos:


        for pedido in pedidos:


            with st.expander(
                f"Pedido #{pedido[0]} - Cliente ID {pedido[1]}"
            ):


                st.write(
                    f"👕 Prenda: {pedido[2]}"
                )


                st.write(
                    f"Cantidad: {pedido[3]}"
                )


                st.write(
                    f"Estado: {pedido[7]}"
                )


                st.write(
                    f"Total: ${pedido[9]}"
                )


                st.write(
                    f"Pagado: ${pedido[10]}"
                )


                st.write(
                    f"Saldo: ${pedido[11]}"
                )



                nuevo_estado = st.selectbox(

                    "Cambiar estado",

                    ESTADOS,

                    index=ESTADOS.index(pedido[7])
                    if pedido[7] in ESTADOS else 0,

                    key=f"estado_{pedido[0]}"

                )



                if st.button(

                    "Actualizar estado",

                    key=f"actualizar_{pedido[0]}"

                ):


                    cambiar_estado(

                        pedido[0],

                        nuevo_estado,

                        st.session_state.usuario

                    )


                    st.success(
                        "Estado actualizado"
                    )


                    st.rerun()



                if st.button(

                    "Cancelar pedido",

                    key=f"eliminar_{pedido[0]}"

                ):


                    eliminar_pedido(

                        pedido[0],

                        st.session_state.usuario

                    )


                    st.warning(
                        "Pedido cancelado"
                    )


                    st.rerun()



    else:


        st.info(
            "No existen pedidos"
        )



    st.divider()



    st.subheader(
        "Crear nuevo pedido"
    )


    clientes = obtener_clientes()



    if clientes:


        opciones = {

            f"{c[1]} - {c[2]}": c[0]

            for c in clientes

        }



        cliente_nombre = st.selectbox(

            "Cliente",

            list(opciones.keys())

        )



        cliente_id = opciones[
            cliente_nombre
        ]



        with st.form(
            "nuevo_pedido"
        ):


            prenda = st.text_input(
                "Prenda"
            )


            cantidad = st.number_input(

                "Cantidad",

                min_value=1,

                value=1

            )


            diseno = st.text_input(
                "Diseño"
            )


            precio = st.number_input(

                "Precio total",

                min_value=0.0

            )


            prioridad = st.selectbox(
                "Prioridad",
                PRIORIDADES
            )


            guardar = st.form_submit_button(

                "Crear pedido"

            )



            if guardar:


                pedido = crear_pedido(

                    cliente_id,

                    prenda,

                    cantidad,

                    diseno,

                    precio,

                    prioridad=prioridad

                )


                if pedido:


                    st.success(
                        f"Pedido creado #{pedido}"
                    )


                    st.rerun()



    else:


        st.warning(
            "Primero cree un cliente"
        )
        # ==========================================
# FINANZAS
# ==========================================

elif menu == "Finanzas":


    st.title(
        "💰 Finanzas"
    )


    resumen = resumen_financiero()



    c1, c2, c3, c4 = st.columns(4)



    c1.metric(

        "Ingresos",

        f"${resumen['ingresos']:,.0f}"

    )


    c2.metric(

        "Gastos",

        f"${resumen['gastos']:,.0f}"

    )


    c3.metric(

        "Balance",

        f"${resumen['balance']:,.0f}"

    )


    c4.metric(

        "Pendiente",

        f"${resumen['pendiente_cobro']:,.0f}"

    )



    st.divider()



    st.subheader(
        "Registrar gasto"
    )



    with st.form(
        "nuevo_gasto"
    ):


        concepto = st.text_input(
            "Concepto"
        )


        categoria = st.text_input(
            "Categoría"
        )


        cantidad = st.number_input(

            "Cantidad",

            min_value=1,

            value=1

        )


        precio = st.number_input(

            "Precio unitario",

            min_value=0.0

        )



        guardar = st.form_submit_button(

            "Guardar gasto"

        )



        if guardar:


            resultado = registrar_gasto(

                concepto,

                categoria,

                cantidad,

                precio,

                st.session_state.usuario

            )


            if resultado:


                st.success(
                    "Gasto registrado"
                )


                st.rerun()



    st.divider()



    st.subheader(
        "Historial de gastos"
    )


    gastos = obtener_gastos()



    if gastos:


        for gasto in gastos:


            st.write(

                f"""

                📅 {gasto[6]}

                🛒 {gasto[1]}

                💵 ${gasto[5]}

                """

            )


            st.divider()



# ==========================================
# REPORTES
# ==========================================

elif menu == "Reportes":


    st.title(
        "📊 Reportes"
    )


    st.write(

        "Generación de reportes del taller"

    )



    if st.button(

        "Generar reporte completo Excel"

    ):


        archivo = exportar_reporte_completo()



        st.success(

            "Reporte generado correctamente"

        )


        st.write(

            archivo

        )



# ==========================================
# FINAL APP
# ==========================================

st.sidebar.divider()


st.sidebar.caption(

    "Sistema Gestión Taller Textil"

        )
