import streamlit as st
from database import inicializar_base_datos
from pedidos import registrar_pedido_ui, listar_pedidos
from finanzas import resumen_financiero, registrar_gasto, obtener_gastos

# Inicializar base de datos al arrancar
inicializar_base_datos()

st.set_page_config(page_title="Gestión Taller Textil", page_icon="🧵", layout="wide")

st.sidebar.title("🧵 Taller Textil")
menu = st.sidebar.radio("Navegación", ["Panel Principal", "Nuevo Pedido", "Ver Pedidos", "Finanzas"])

if menu == "Panel Principal":
    st.title("🧵 Panel de Control")
    resumen = resumen_financiero()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos (Señas)", f"${resumen['ingresos']:,.0f}")
    c2.metric("Gastos Totales", f"${resumen['gastos']:,.0f}")
    c3.metric("Saldo Pendiente de Cobro", f"${resumen['pendiente_cobro']:,.0f}")
    
    st.divider()
    st.info("💡 Usá el menú de la izquierda para registrar nuevos pedidos con múltiples talles o revisar las finanzas del taller.")

elif menu == "Nuevo Pedido":
    registrar_pedido_ui()

elif menu == "Ver Pedidos":
    listar_pedidos()

elif menu == "Finanzas":
    st.subheader("💰 Control Financiero y Gastos")
    
    resumen = resumen_financiero()
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos (Señas)", f"${resumen['ingresos']:,.0f}")
    c2.metric("Gastos", f"${resumen['gastos']:,.0f}")
    c3.metric("Balance Real", f"${resumen['balance']:,.0f}")
    
    st.divider()
    st.markdown("### Registrar Nuevo Gasto")
    with st.form("form_gasto", clear_on_submit=True):
        concepto = st.text_input("Concepto (ej: Insumos, Telas, Tintas)")
        categoria = st.selectbox("Categoría", ["Materia Prima", "Herramientas", "Servicios", "Otros"])
        c_cant = st.number_input("Cantidad", min_value=1, value=1)
        c_precio = st.number_input("Precio Unitario", min_value=0.0, step=100.0)
        
        if st.form_submit_button("Guardar Gasto"):
            if concepto.strip():
                registrar_gasto(concepto, categoria, c_cant, c_precio)
                st.success("Gasto registrado con éxito.")
                st.rerun()
            else:
                st.error("Ingresá un concepto válido.")

    st.markdown("### Historial de Gastos")
    gastos = obtener_gastos()
    if gastos:
        for g in gastos:
            st.text(f"• [{g[5]}] {g[1]} ({g[2]}) — Cant: {g[3]} — Total: ${g[5]:,.0f}")
    else:
        st.info("No hay gastos registrados.")
