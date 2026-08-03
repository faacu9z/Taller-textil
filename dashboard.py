"""
==========================================
DASHBOARD (Versión Simplificada)
Gestión Taller Textil
==========================================
"""

import streamlit as st
from database import conectar

# ==========================================
# ESTADÍSTICAS SIMPLIFICADAS
# ==========================================

def obtener_estadisticas_rapidas():
    conexion = conectar()
    cursor = conexion.cursor()
    
    datos = {}
    try:
        # Total pedidos activos
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'Activo'")
        datos["activos"] = cursor.fetchone()[0] or 0

        # Total entregados
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'Entregado'")
        datos["entregados"] = cursor.fetchone()[0] or 0

        # Total ingresos cobrados (Suma de señas o pagos si los hubiera)
        cursor.execute("SELECT SUM(senia) FROM pedidos")
        datos["senias_recaudadas"] = cursor.fetchone()[0] or 0

        # Total pendiente de cobro
        cursor.execute("SELECT SUM(saldo) FROM pedidos WHERE estado = 'Activo'")
        datos["pendiente"] = cursor.fetchone()[0] or 0

        return datos
    finally:
        conexion.close()


# ==========================================
# TARJETA MÉTRICA
# ==========================================

def tarjeta(titulo, valor, icono=""):
    st.markdown(
        f"""
        <div style="
            background:white;
            padding:20px;
            border-radius:12px;
            border:1px solid #ddd;
            text-align:center;
            color: #31333F;
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

def dashboard_completo():
    st.title("🧵 Panel de Control")

    stats = obtener_estadisticas_rapidas()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tarjeta("Pedidos Activos", stats["activos"], "📦")

    with col2:
        tarjeta("Entregados", stats["entregados"], "✅")

    with col3:
        tarjeta("Señas / Ingresos", f"${stats['senias_recaudadas']:,.0f}", "💵")

    with col4:
        tarjeta("Saldo Pendiente", f"${stats['pendiente']:,.0f}", "⏳")

    st.divider()
    st.info("💡 Consejo: Usá la sección de **Pedidos** en el menú lateral para registrar nuevos trabajos, ver los enlaces rápidos de WhatsApp o marcar pedidos como entregados.")
