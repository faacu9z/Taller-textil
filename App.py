"""
==========================================
APP PRINCIPAL (Versión Simplificada)
Gestión Taller Textil
==========================================

Ejecutar:
streamlit run App.py
==========================================
"""

import streamlit as st
import pandas as pd

from auth import (
    login,
    registrar_usuario,
    crear_admin
)

from pedidos import (
    crear_pedido,
    obtener_pedidos,
    buscar_pedidos,
    cambiar_estado_pedido,
    eliminar_pedido_definitivo,
    generar_link_whatsapp
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
    st.title("🧵 Gestión Taller Textil")
    
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar", use_container_width=True):
            datos = login(usuario, password)

            if datos:
                st.session_state.usuario = usuario
                st.success("Ingreso correcto")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    st.divider()

    with st.expander("Registrar usuario nuevo"):
        nuevo_usuario = st.text_input("Nuevo usuario")
        nueva_password = st.text_input("Nueva contraseña", type="password")

        if st.button("Crear usuario"):
            ok, mensaje = registrar_usuario(nuevo_usuario, nueva_password)
            if ok:
                st.success(mensaje)
            else:
                st.error(mensaje)


# ==========================================
# CONTROL LOGIN
# ==========================================

if st.session_state.usuario is None:
    pantalla_login()
    st.stop()


# ==========================================
# MENU PRINCIPAL
# ==========================================

st.sidebar.title("🧵 Taller Textil")
st.sidebar.write(f"Usuario: {st.session_state.usuario}")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.usuario = None
    st.rerun()

menu = st.sidebar.radio(
    "Secciones",
    [
        "Dashboard",
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
# PEDIDOS (Simplificado y optimizado)
# ==========================================

elif menu == "Pedidos":
    st.title("📦 Gestión de Pedidos")

    # Pestañas internas para Activos vs Cancelados
    pestania1, pestania2 = st.tabs(["Pedidos Activos", "Nuevo Pedido"])

    with pestania1:
        busqueda = st.text_input("Buscar pedido por nombre, WhatsApp o archivo...")

        if busqueda:
            pedidos = buscar_pedidos(busqueda, estado="Activo")
        else:
            pedidos = obtener_pedidos(estado="Activo")

        st.subheader("Listado de Pedidos Activos")

        if pedidos:
            for pedido in pedidos:
                # Extraer datos de la tupla / row
                p_id = pedido["id"]
                nro_archivo = pedido["nro_archivo"] or "S/N"
                nombre = pedido["cliente_nombre"]
                whatsapp = pedido["cliente_whatsapp"]
                precio = pedido["precio_total"]
                senia = pedido["senia"]
                saldo = pedido["saldo"]
                obs = pedido["observaciones"]
                fecha = pedido["fecha_creacion"]

                link_wa = generar_link_whatsapp(whatsapp, f"Hola {nombre}, te escribo por tu pedido #{p_id} de Taller Textil.")

                with st.expander(f"Archivo #{nro_archivo} - {nombre} (Saldo: ${saldo:,.0f})"):
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.write(f"👤 **Cliente:** {nombre}")
                        st.write(f"📱 **WhatsApp:** {whatsapp} ([Abrir Chat]({link_wa}))")
                        st.write(f"📂 **Nro de Archivo:** {nro_archivo}")
                        st.write(f"📅 **Fecha:** {fecha}")

                    with col_info2:
                        st.write(f"💵 **Precio Total:** ${precio:,.0f}")
                        st.write(f"📥 **Seña:** ${senia:,.0f}")
                        st.markdown(f"⏳ **Saldo Pendiente:** <span style='color:red; font-weight:bold;'>${saldo:,.0f}</span>", unsafe_allow_html=True)

                    if obs:
                        st.info(f"📝 **Observaciones:** {obs}")

                    st.divider()

                    # Acciones rápidas
                    col_accion1, col_accion2 = st.columns(2)
                    with col_accion1:
                        if st.button("Marcar como Entregado / Finalizar", key=f"fin_{p_id}"):
                            cambiar_estado_pedido(p_id, "Entregado")
                            st.success("Pedido actualizado")
                            st.rerun()

                    with col_accion2:
                        if st.button("🗑️ Eliminar pedido", key=f"del_{p_id}"):
                            eliminar_pedido_definitivo(p_id)
                            st.warning("Pedido eliminado")
                            st.rerun()
        else:
            st.info("No hay pedidos activos registrados.")

    with pestania2:
        st.subheader("Crear Nuevo Pedido")

        with st.form("nuevo_pedido_form"):
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                cliente_nombre = st.text_input("Nombre y Apellido del Cliente")
                cliente_whatsapp = st.text_input("WhatsApp (ej: 3704123456)")
                nro_archivo = st.text_input("Número de Archivo (Opcional)")

            with col_f2:
                precio_total = st.number_input("Precio Total ($)", min_value=0.0, step=100.0)
                senia = st.number_input("Seña / Adelanto ($)", min_value=0.0, step=100.0)
                tomado_por = st.text_input("Tomado por (Tu nombre / Usuario)", value=st.session_state.usuario)

            observaciones = st.text_area("Observaciones Generales")

            st.markdown("---")
            st.markdown("### 👕 Detalle de Prendas (Nombres, Talles y Números)")
            
            # Simulamos una tabla dinámica simple para ingresar prendas
            num_prendas = st.number_input("Cantidad de prendas en este pedido", min_value=1, max_value=50, value=1)
            
            prendas_ingresadas = []
            for i in range(int(num_prendas)):
                cols_p = st.columns(3)
                with cols_p[0]:
                    nom_apo = st.text_input(f"Nombre / Apodo #{i+1}", key=f"nom_{i}")
                with cols_p[1]:
                    talle = st.text_input(f"Talle #{i+1}", key=f"tal_{i}")
                with cols_p[2]:
                    nro = st.text_input(f"Número #{i+1}", key=f"nro_{i}")
                
                if nom_apo or talle or nro:
                    prendas_ingresadas.append({
                        "nombre": nom_apo,
                        "talle": talle,
                        "numero": nro
                    })

            imagenes_subidas = st.file_uploader("Adjuntar Imágenes / Referencias (Opcional)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

            guardar_btn = st.form_submit_button("Guardar Pedido Completo", use_container_width=True)

            if guardar_btn:
                if not cliente_nombre or not cliente_whatsapp:
                    st.error("El nombre y el WhatsApp del cliente son obligatorios.")
                else:
                    id_creado = crear_pedido(
                        nro_archivo=nro_archivo,
                        cliente_nombre=cliente_nombre,
                        cliente_whatsapp=cliente_whatsapp,
                        tomado_por=tomado_por,
                        precio_total=precio_total,
                        senia=senia,
                        observaciones=observaciones,
                        prendas=prendas_ingresadas,
                        imagenes=imagenes_subidas
                    )

                    if id_creado:
                        st.success(f"¡Pedido #${id_creado} creado con éxito!")
                        st.rerun()
                    else:
                        st.error("Hubo un error al guardar el pedido en la base de datos.")


# ==========================================
# FINANZAS
# ==========================================

elif menu == "Finanzas":
    st.title("💰 Finanzas")

    resumen = resumen_financiero()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingresos", f"${resumen['ingresos']:,.0f}")
    c2.metric("Gastos", f"${resumen['gastos']:,.0f}")
    c3.metric("Balance", f"${resumen['balance']:,.0f}")
    c4.metric("Pendiente", f"${resumen['pendiente_cobro']:,.0f}")

    st.divider()

    st.subheader("Registrar Gasto")

    with st.form("nuevo_gasto"):
        concepto = st.text_input("Concepto")
        categoria = st.text_input("Categoría")
        cantidad = st.number_input("Cantidad", min_value=1.0, value=1.0)
        precio = st.number_input("Precio unitario", min_value=0.0)

        guardar = st.form_submit_button("Guardar gasto")

        if guardar:
            resultado = registrar_gasto(
                concepto,
                categoria,
                cantidad,
                precio,
                st.session_state.usuario
            )

            if resultado:
                st.success("Gasto registrado")
                st.rerun()
            else:
                st.error("Error al registrar el gasto")

    st.divider()
    st.subheader("Historial de Gastos")
    gastos = obtener_gastos()

    if gastos:
        for gasto in gastos:
            st.write(f"📅 {gasto['fecha']} | 🛒 **{gasto['concepto']}** ({gasto['categoria']}) - 💵 **${gasto['total']:,.0f}**")
            st.divider()


# ==========================================
# REPORTES
# ==========================================

elif menu == "Reportes":
    st.title("📊 Reportes")
    st.write("Generación de reportes generales del taller.")

    if st.button("Generar reporte completo Excel"):
        archivo = exportar_reporte_completo()
        st.success("Reporte generado correctamente")
        st.write(f"Ruta del archivo: {archivo}")


# ==========================================
# FINAL APP
# ==========================================

st.sidebar.divider()
st.sidebar.caption("Sistema Gestión Taller Textil v2.0")
