import streamlit as st
import sqlite3
from datetime import datetime
import urllib.parse

DB_NAME = "database.db"

# ==========================================
# 1. CONFIGURACIÓN Y BASE DE DATOS
# ==========================================
def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def inicializar_base_datos():
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Tabla principal de pedidos (incluye quién lo tomó)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            telefono_cliente TEXT NOT NULL,
            vendedor TEXT NOT NULL,
            fecha TEXT NOT NULL,
            estado TEXT NOT NULL, -- 'Activo' o 'Entregado'
            senia REAL DEFAULT 0,
            saldo REAL DEFAULT 0,
            total REAL DEFAULT 0
        )
    """)
    
    # Tabla de detalles (múltiples talles, prendas y cantidades por pedido)
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
            fecha TEXT NOT NULL,
            registrado_por TEXT
        )
    """)
    conexion.commit()
    conexion.close()

inicializar_base_datos()

# Configuración visual de Streamlit
st.set_page_config(page_title="Gestión Taller Textil", page_icon="🧵", layout="wide")

# ==========================================
# 2. BARRA LATERAL Y AUTENTICACIÓN RÁPIDA
# ==========================================
st.sidebar.title("🧵 Taller Textil")
st.sidebar.markdown("---")

# Control de quién está operando el sistema
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = "Facundo"

st.sidebar.markdown("👤 **Usuario Actual:**")
usuario_input = st.sidebar.text_input("Quién sos?", value=st.session_state.usuario_actual, label_visibility="collapsed")
if usuario_input:
    st.session_state.usuario_actual = usuario_input

st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegación", ["Panel Principal", "Nuevo Pedido", "Ver Pedidos", "Finanzas"])

# ==========================================
# 3. LÓGICA DE FINANZAS (CONSULTAS)
# ==========================================
def obtener_resumen_financiero():
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Ingresos (suma de señas)
    cursor.execute("SELECT SUM(senia) FROM pedidos")
    ingresos = cursor.fetchone()[0] or 0.0
    
    # Saldo pendiente de cobro
    cursor.execute("SELECT SUM(saldo) FROM pedidos WHERE estado = 'Activo'")
    pendiente = cursor.fetchone()[0] or 0.0
    
    # Gastos totales
    cursor.execute("SELECT SUM(total) FROM gastos")
    gastos = cursor.fetchone()[0] or 0.0
    
    conexion.close()
    return {"ingresos": ingresos, "gastos": gastos, "balance": ingresos - gastos, "pendiente": pendiente}

# ==========================================
# 4. PANTALLAS DE LA APLICACIÓN
# ==========================================

if menu == "Panel Principal":
    st.title("🧵 Panel de Control")
    st.write(f"Bienvenido de nuevo, **{st.session_state.usuario_actual}**. Este es el estado actual del taller:")
    
    resumen = obtener_resumen_financiero()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingresos (Señas)", f"${resumen['ingresos']:,.0f}")
    c2.metric("Gastos Totales", f"${resumen['gastos']:,.0f}")
    c3.metric("Balance Real", f"${resumen['balance']:,.0f}")
    c4.metric("Saldo a Cobrar", f"${resumen['pendiente']:,.0f}")
    
    st.divider()
    st.info("💡 Usá el menú lateral para cargar nuevos pedidos con múltiples talles y cantidades, o revisar el historial.")

elif menu == "Nuevo Pedido":
    st.title("📝 Registrar Nuevo Pedido")
    st.caption(f"Pedido tomado por: **{st.session_state.usuario_actual}**")
    
    with st.form("form_pedido", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre_cliente = st.text_input("Nombre del Cliente*")
        with col2:
            telefono_cliente = st.text_input("WhatsApp / Teléfono* (ej: 3704...)")
            
        st.divider()
        st.markdown("### 👕 Detalle de Prendas y Talles")
        
        if "items_pedido" not in st.session_state:
            st.session_state.items_pedido = [{"prenda": "Remera", "talle": "L", "cantidad": 1, "precio": 0.0}]

        # Gestión dinámica de filas de talles
        for i, item in enumerate(st.session_state.items_pedido):
            cc1, cc2, cc3, cc4 = st.columns([2, 1, 1, 1])
            with cc1:
                st.session_state.items_pedido[i]["prenda"] = st.text_input(f"Prenda {i+1}", value=item["prenda"], key=f"pr_{i}")
            with cc2:
                st.session_state.items_pedido[i]["talle"] = st.text_input(f"Talle {i+1}", value=item["talle"], key=f"ta_{i}")
            with cc3:
                st.session_state.items_pedido[i]["cantidad"] = st.number_input(f"Cant {i+1}", min_value=1, value=item["cantidad"], key=f"ca_{i}")
            with cc4:
                st.session_state.items_pedido[i]["precio"] = st.number_input(f"Precio U. {i+1}", min_value=0.0, value=item["precio"], step=100.0, key=f"pu_{i}")

        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.form_submit_button("➕ Agregar otro talle/prenda"):
            st.session_state.items_pedido.append({"prenda": "Remera", "talle": "M", "cantidad": 1, "precio": 0.0})
            st.rerun()

        st.divider()
        senia_abonada = st.number_input("Seña Abonada ($)", min_value=0.0, step=100.0)
        
        guardar = st.form_submit_button("Guardar Pedido Definitivo 💾", use_container_width=True)
        
        if guardar:
            if not nombre_cliente.strip() or not telefono_cliente.strip():
                st.error("Completá el nombre y teléfono del cliente.")
            else:
                total_global = sum(it["cantidad"] * it["precio"] for it in st.session_state.items_pedido)
                saldo_restante = total_global - senia_abonada
                fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                conexion = conectar()
                cursor = conexion.cursor()
                try:
                    cursor.execute(
                        """
                        INSERT INTO pedidos (nombre_cliente, telefono_cliente, vendedor, fecha, estado, senia, saldo, total)
                        VALUES (?, ?, ?, ?, 'Activo', ?, ?, ?)
                        """,
                        (nombre_cliente.strip(), telefono_cliente.strip(), st.session_state.usuario_actual, fecha_actual, senia_abonada, saldo_restante, total_global)
                    )
                    pedido_id = cursor.lastrowid
                    
                    for it in st.session_state.items_pedido:
                        cursor.execute(
                            """
                            INSERT INTO detalle_pedidos (pedido_id, prenda, talle, cantidad, precio_unitario)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (pedido_id, it["prenda"], it["talle"], it["cantidad"], it["precio"])
                        )
                        
                    conexion.commit()
                    st.success("¡Pedido guardado con éxito!")
                    st.session_state.items_pedido = [{"prenda": "Remera", "talle": "L", "cantidad": 1, "precio": 0.0}]
                    st.rerun()
                except Exception as e:
                    conexion.rollback()
                    st.error(f"Error al guardar en base de datos: {e}")
                finally:
                    conexion.close()

elif menu == "Ver Pedidos":
    st.title("📦 Gestión y Estado de Pedidos")
    
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre_cliente, telefono_cliente, vendedor, fecha, estado, senia, saldo, total FROM pedidos ORDER BY id DESC")
    pedidos = cursor.fetchall()
    conexion.close()
    
    if not pedidos:
        st.info("No hay pedidos registrados.")
    else:
        for p in pedidos:
            p_id, cliente, tel, vendedor, fecha, estado, senia, saldo, total = p
            
            # Buscar talles de este pedido
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT prenda, talle, cantidad, precio_unitario FROM detalle_pedidos WHERE pedido_id = ?", (p_id,))
            detalles = cursor.fetchall()
            conexion.close()
            
            with st.expander(f"Pedido #{p_id} — {cliente} ({estado}) | Tomado por: {vendedor}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"📅 **Fecha:** {fecha}")
                    st.write(f"📱 **Celular:** {tel}")
                    st.write(f"👤 **Vendedor:** {vendedor}")
                with c2:
                    st.write(f"💵 **Seña:** ${senia:,.0f}")
                    st.write(f"⏳ **Saldo:** ${saldo:,.0f}")
                    st.write(f"🏷️ **Total:** ${total:,.0f}")
                
                st.markdown("---")
                st.markdown("**Desglose de Talles y Prendas:**")
                for det in detalles:
                    prenda, talle, cant, precio_u = det
                    st.text(f"• {cant}x {prenda} (Talle: {talle}) — Unitario: ${precio_u:,.0f}")

                # Botones de acción (WhatsApp, Entregar, Eliminar)
                b1, b2, b3 = st.columns(3)
                with b1:
                    texto_wa = f"Hola {cliente}! Te escribimos del taller textil por tu pedido #{p_id}. El total es ${total:,.0f}, abonaste ${senia:,.0f} y te queda un saldo de ${saldo:,.0f}."
                    link_wa = f"https://wa.me/549{tel.replace(' ', '')}?text={urllib_parse.quote(texto_wa)}"
                    st.markdown(f"[💬 Enviar WhatsApp]({link_wa})", unsafe_allow_html=True)
                
                with b2:
                    if estado == "Activo":
                        if st.button(f"Marcar Entregado #{p_id}", key=f"ent_{p_id}"):
                            conexion = conectar()
                            cursor = conexion.cursor()
                            cursor.execute("UPDATE pedidos SET estado = 'Entregado', saldo = 0 WHERE id = ?", (p_id,))
                            conexion.commit()
                            conexion.close()
                            st.success("¡Marcado como entregado!")
                            st.rerun()
                with b3:
                    if st.button(f"Eliminar #{p_id}", key=f"del_{p_id}"):
                        conexion = conectar()
                        cursor = conexion.cursor()
                        cursor.execute("DELETE FROM pedidos WHERE id = ?", (p_id,))
                        conexion.commit()
                        conexion.close()
                        st.warning("Pedido eliminado.")
                        st.rerun()

elif menu == "Finanzas":
    st.title("💰 Finanzas y Gastos del Taller")
    
    resumen = obtener_resumen_financiero()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos por Señas", f"${resumen['ingresos']:,.0f}")
    c2.metric("Gastos Totales", f"${resumen['gastos']:,.0f}")
    c3.metric("Balance Neto", f"${resumen['balance']:,.0f}")
    
    st.divider()
    st.markdown("### Registrar Nuevo Gasto")
    with st.form("form_gasto", clear_on_submit=True):
        concepto = st.text_input("Concepto (ej: Compra de Telas, Tintas, Service)")
        categoria = st.selectbox("Categoría", ["Materia Prima", "Insumos", "Herramientas", "Servicios", "Otros"])
        cant = st.number_input("Cantidad", min_value=1, value=1)
        precio_u = st.number_input("Precio Unitario ($)", min_value=0.0, step=100.0)
        
        if st.form_submit_button("Guardar Gasto"):
            if concepto.strip():
                total_gasto = cant * precio_u
                fecha_gasto = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                conexion = conectar()
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    INSERT INTO gastos (concepto, categoria, cantidad, precio_unitario, total, fecha, registrado_por)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (concepto.strip(), categoria, cant, precio_u, total_gasto, fecha_gasto, st.session_state.usuario_actual)
                )
                conexion.commit()
                conexion.close()
                st.success("Gasto registrado correctamente.")
                st.rerun()
            else:
                st.error("Escribí un concepto válido.")

    st.markdown("### Historial de Gastos")
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT concepto, categoria, cantidad, total, fecha, registrado_por FROM gastos ORDER BY id DESC")
    gastos = cursor.fetchall()
    conexion.close()
    
    if gastos:
        for g in gastos:
            st.text(f"• [{g[4]}] {g[0]} ({g[1]}) — Cant: {g[2]} — Total: ${g[3]:,.0f} (Registrado por: {g[5]})")
    else:
        st.info("No hay gastos registrados.")
