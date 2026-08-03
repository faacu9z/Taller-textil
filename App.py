import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from pathlib import Path

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión de Taller Textil", page_icon="🛒", layout="wide")

# --- RUTA DE GUARDADO LOCAL AUTOMÁTICA ---
CARPETA_DATOS = Path.home() / "TallerTextilData"
CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
ARCH_EXCEL = CARPETA_DATOS / "base_datos_taller.xlsx"

# --- FUNCIONES DE PERSISTENCIA LOCAL (EXCEL) ---
def cargar_datos_iniciales():
    if "usuarios" not in st.session_state:
        st.session_state.usuarios = {"admin": "1234"}

    # Cargar Pedidos
    if "pedidos" not in st.session_state:
        if ARCH_EXCEL.exists():
            try:
                df_p = pd.read_excel(ARCH_EXCEL, sheet_name="Pedidos")
                if "Historial_Pagos" in df_p.columns:
                    df_p["Historial_Pagos"] = df_p["Historial_Pagos"].apply(lambda x: eval(x) if pd.notnull(x) and x != "" else [])
                st.session_state.pedidos = df_p
            except:
                st.session_state.pedidos = pd.DataFrame(columns=[
                    "ID_Base", "Cliente", "Telefono", "Prenda", "Cantidad", "Diseno", "ArchivoPC", "TablaTalles", 
                    "Observaciones", "Imagen", "Estado", "Vendedor", "Fecha_Obj", "Fecha", "Hora", "Anio",
                    "Precio_Total", "Sena", "Total_Pagado", "Saldo", "Historial_Pagos"
                ])
        else:
            st.session_state.pedidos = pd.DataFrame(columns=[
                "ID_Base", "Cliente", "Telefono", "Prenda", "Cantidad", "Diseno", "ArchivoPC", "TablaTalles", 
                "Observaciones", "Imagen", "Estado", "Vendedor", "Fecha_Obj", "Fecha", "Hora", "Anio",
                "Precio_Total", "Sena", "Total_Pagado", "Saldo", "Historial_Pagos"
            ])

    # Cargar Gastos
    if "gastos" not in st.session_state:
        if ARCH_EXCEL.exists():
            try:
                st.session_state.gastos = pd.read_excel(ARCH_EXCEL, sheet_name="Gastos")
            except:
                st.session_state.gastos = pd.DataFrame(columns=["Fecha_Obj", "Fecha", "Item", "Cantidad", "Precio_Unitario", "Total"])
        else:
            st.session_state.gastos = pd.DataFrame(columns=["Fecha_Obj", "Fecha", "Item", "Cantidad", "Precio_Unitario", "Total"])

def guardar_en_disco():
    try:
        with pd.ExcelWriter(ARCH_EXCEL, engine="openpyxl") as writer:
            df_p_guardar = st.session_state.pedidos.copy()
            if "Historial_Pagos" in df_p_guardar.columns:
                df_p_guardar["Historial_Pagos"] = df_p_guardar["Historial_Pagos"].astype(str)
            
            df_p_guardar.to_excel(writer, sheet_name="Pedidos", index=False)
            st.session_state.gastos.to_excel(writer, sheet_name="Gastos", index=False)
    except ModuleNotFoundError:
        pass

cargar_datos_iniciales()

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: 500; }
    .card-pedido { background: white; padding: 15px 20px; border-radius: 10px; border: 1px solid #EAEAEA; margin-bottom: 12px; }
    .metric-card { background: white; padding: 20px; border-radius: 10px; border: 1px solid #EAEAEA; text-align: center; }
    .col-bloque { background: white; padding: 20px; border-radius: 10px; border: 1px solid #EAEAEA; height: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES DE NAVEGACIÓN ---
if "vendedor_actual" not in st.session_state: st.session_state.vendedor_actual = None
if "pedido_seleccionado" not in st.session_state: st.session_state.pedido_seleccionado = None

estados_posibles = ["1. Ingreso de pedido", "2. Diseño y confirmación de cliente", "3. En plancha", "4. En costura", "5. Control de calidad", "6. Entregado"]
tipos_prenda = ["camiseta sola", "camiseta + short", "sudadera", "sudadera + short", "chomba deportiva", "conjunto de invierno", "short", "pechera", "bandera", "gorra", "campera"]
medios_pago = ["Efectivo", "Transferencia", "Tarjeta", "QR"]

# --- LOGIN ---
if st.session_state.vendedor_actual is None:
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown("<h2 style='text-align: center;'>🧵 Taller Textil</h2>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrar Vendedor"])
        with tab1:
            user_ingreso = st.text_input("Usuario")
            pass_ingreso = st.text_input("Contraseña", type="password")
            if st.button("Entrar", type="primary"):
                if user_ingreso in st.session_state.usuarios and st.session_state.usuarios[user_ingreso] == pass_ingreso:
                    st.session_state.vendedor_actual = user_ingreso
                    st.rerun()
                else:
                    st.error("Datos incorrectos.")
        with tab2:
            nuevo_user = st.text_input("Nuevo Usuario", key="reg_user")
            nuevo_pass = st.text_input("Nueva Contraseña", type="password", key="reg_pass")
            if st.button("Registrar"):
                if nuevo_user and nuevo_pass:
                    if nuevo_user in st.session_state.usuarios: st.warning("El usuario ya existe.")
                    else:
                        st.session_state.usuarios[nuevo_user] = nuevo_pass
                        st.success("¡Registrado con éxito!")
    st.stop()

# --- VISTA DETALLADA DEL PEDIDO ---
if st.session_state.pedido_seleccionado is not None:
    idx = st.session_state.pedido_seleccionado
    if idx not in st.session_state.pedidos.index:
        st.session_state.pedido_seleccionado = None
        st.rerun()
        
    row = st.session_state.pedidos.loc[idx]
    
    col_v1, col_v2, col_v3 = st.columns([2, 5, 2])
    with col_v1:
        if st.button("← Volver a la lista"):
            st.session_state.pedido_seleccionado = None
            st.rerun()
    with col_v3:
        with st.popover("🗑️ Eliminar Pedido"):
            st.error("¿Estás seguro de que quieres eliminar este pedido?")
            if st.button("Sí, Confirmar Eliminación", type="primary", key="del_ped"):
                st.session_state.pedidos = st.session_state.pedidos.drop(idx)
                guardar_en_disco()
                st.session_state.pedido_seleccionado = None
                st.rerun()

    st.markdown(f"## 📂 Detalle del Pedido: #{row['ID_Base']:03d}")
    
    col_izq, col_der = st.columns([1, 1.3])
    with col_izq:
        st.markdown("<div class='col-bloque'>", unsafe_allow_html=True)
        st.markdown("### 📋 Datos Generales")
        
        num_wsp = ''.join(filter(str.isdigit, str(row['Telefono'])))
        link_wsp = f"https://wa.me/{num_wsp}" if num_wsp else "#"
        st.markdown(f"**👤 Cliente:** {row['Cliente']} | **📲 WhatsApp:** <a href='{link_wsp}' target='_blank'>{row['Telefono']} (Enviar msj)</a>", unsafe_allow_html=True)
        
        st.write(f"**🤝 Vendedor:** {row['Vendedor']} | **📅 Ingreso:** {row['Fecha']}")
        st.write(f"**📁 Archivo en PC:** {row['ArchivoPC']}")
        st.divider()
        st.write(f"**👕 Prenda:** {row['Prenda']} (x{row['Cantidad']})")
        st.write(f"**🎨 Diseño:** {row['Diseno']}")
        st.divider()
        nuevo_est_det = st.selectbox("📌 Estado Actual", estados_posibles, index=estados_posibles.index(row["Estado"]))
        if nuevo_est_det != row["Estado"]:
            st.session_state.pedidos.at[idx, "Estado"] = nuevo_est_det
            guardar_en_disco()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_der:
        st.markdown("<div class='col-bloque'>", unsafe_allow_html=True)
        st.markdown("### 💰 Finanzas y Pagos")
        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("Precio Acordado", f"${row['Precio_Total']:,.0f}")
        c_m2.metric("Abonado", f"${row['Total_Pagado']:,.0f}")
        c_m3.metric("Falta Pagar", f"${row['Saldo']:,.0f}")

        if isinstance(row['Historial_Pagos'], list) and len(row['Historial_Pagos']) > 0:
            df_historial = pd.DataFrame(row['Historial_Pagos']).drop(columns=["Fecha_Obj"], errors="ignore")
            st.dataframe(df_historial, use_container_width=True, hide_index=True)
            
        if row['Saldo'] > 0:
            with st.expander("➕ Pagar Saldo"):
                with st.form(f"form_pago_{idx}"):
                    monto_a_pagar = st.number_input("Monto ($)", min_value=0.0, max_value=float(row['Saldo']), value=float(row['Saldo']))
                    medio_pago_saldo = st.selectbox("Medio de Pago", medios_pago)
                    if st.form_submit_button("Confirmar"):
                        ahora = datetime.utcnow() - timedelta(hours=3)
                        nuevo_pago = {"Fecha_Obj": ahora, "Fecha": ahora.strftime("%d/%m/%Y"), "Hora": ahora.strftime("%H:%M"), "Vendedor": st.session_state.vendedor_actual, "Concepto": "Pago de Saldo", "Monto": monto_a_pagar, "Medio": medio_pago_saldo}
                        historial_actual = row['Historial_Pagos'] if isinstance(row['Historial_Pagos'], list) else []
                        historial_actual.append(nuevo_pago)
                        st.session_state.pedidos.at[idx, "Historial_Pagos"] = historial_actual
                        st.session_state.pedidos.at[idx, "Total_Pagado"] = row['Total_Pagado'] + monto_a_pagar
                        st.session_state.pedidos.at[idx, "Saldo"] = row['Precio_Total'] - (row['Total_Pagado'] + monto_a_pagar)
                        guardar_en_disco()
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- BARRA SUPERIOR ---
col_top1, col_top2 = st.columns([6, 1])
with col_top1: st.title("🧵 Gestión de Producción (Local)")
with col_top2:
    st.write(f"👤 **{st.session_state.vendedor_actual}**")
    if st.button("Salir"):
        st.session_state.vendedor_actual = None
        st.rerun()

tab_nuevo, tab_lista, tab_finanzas = st.tabs(["➕ Nuevo Pedido", "📋 Pedidos en Curso", "📊 Finanzas y Stock"])

# --- PESTAÑA 1: NUEVO PEDIDO ---
with tab_nuevo:
    with st.form("form_nuevo_pedido", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cliente = st.text_input("Nombre del Cliente")
            telefono = st.text_input("WhatsApp (Ej: 549112345678)")
            prenda = st.selectbox("Tipo de Prenda", tipos_prenda)
            precio_tot = st.number_input("Precio Total ($)", min_value=0.0, step=1000.0)
        with col_f2:
            cantidad = st.number_input("Cantidad", min_value=1, value=10)
            diseno = st.text_input("Diseño")
            archivo_pc = st.text_input("Nº / Nombre de Archivo en PC", value="S/N")
            sena = st.number_input("Seña Inicial ($)", min_value=0.0, step=1000.0)
            mp_sena = st.selectbox("Medio de Pago (Seña)", medios_pago)

        if st.form_submit_button("Guardar Pedido", type="primary") and cliente:
            ahora = datetime.utcnow() - timedelta(hours=3)
            historial_inicial = [{"Fecha_Obj": ahora, "Fecha": ahora.strftime("%d/%m/%Y"), "Hora": ahora.strftime("%H:%M"), "Vendedor": st.session_state.vendedor_actual, "Concepto": "Seña", "Monto": sena, "Medio": mp_sena}] if sena > 0 else []
            
            nuevo_df = pd.DataFrame([{
                "ID_Base": len(st.session_state.pedidos) + 1, "Cliente": cliente, "Telefono": telefono, "Prenda": prenda, "Cantidad": cantidad,
                "Diseno": diseno, "ArchivoPC": archivo_pc, "TablaTalles": str([{"Nombre": "", "Talle": "", "Número": "", "Short": False}]),
                "Observaciones": "", "Imagen": None, "Estado": estados_posibles[0], "Vendedor": st.session_state.vendedor_actual,
                "Fecha_Obj": ahora, "Fecha": ahora.strftime("%d/%m/%Y"), "Hora": ahora.strftime("%H:%M"), "Anio": ahora.strftime("%Y"),
                "Precio_Total": precio_tot, "Sena": sena, "Total_Pagado": sena, "Saldo": precio_tot - sena, "Historial_Pagos": historial_inicial
            }])
            
            if st.session_state.pedidos.empty:
                st.session_state.pedidos = nuevo_df
            else:
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, nuevo_df], ignore_index=True)
            
            guardar_en_disco()
            st.success("¡Pedido guardado con éxito!")

# --- PESTAÑA 2: LISTA DE PEDIDOS (CON BUSCADOR) ---
with tab_lista:
    busqueda = st.text_input("🔍 Buscar pedido (Nombre, Prenda, Archivo o ID)")
    
    df_mostrar = st.session_state.pedidos
    if not df_mostrar.empty and busqueda:
        busqueda = busqueda.lower()
        mask = (
            df_mostrar["Cliente"].astype(str).str.lower().str.contains(busqueda) |
            df_mostrar["Prenda"].astype(str).str.lower().str.contains(busqueda) |
            df_mostrar["ArchivoPC"].astype(str).str.lower().str.contains(busqueda) |
            df_mostrar["ID_Base"].astype(str).str.contains(busqueda)
        )
        df_mostrar = df_mostrar[mask]

    if df_mostrar.empty:
        st.info("No hay pedidos.")
    else:
        for idx, row in df_mostrar.sort_values(by="Fecha_Obj", ascending=False).iterrows():
            with st.container():
                st.markdown('<div class="card-pedido">', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1.5, 3, 2, 2.5])
                with c1:
                    if st.button(f"📄 #{row['ID_Base']:03d}", key=f"btn_p_{idx}"):
                        st.session_state.pedido_seleccionado = idx
                        st.rerun()
                with c2: st.write(f"**{row['Cliente']}** - {row['Prenda']}")
                with c3: st.write(f"*{row['Estado']}*")
                with c4: st.markdown(f"${row['Total_Pagado']:,.0f} <br> ${row['Saldo']:,.0f}", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 3: FINANZAS Y STOCK ---
with tab_finanzas:
    st.markdown("### 📊 Control de Finanzas y Stock")
    
    total_ingresos = st.session_state.pedidos["Total_Pagado"].sum() if not st.session_state.pedidos.empty else 0.0
    total_gastos = st.session_state.gastos["Total"].sum() if not st.session_state.gastos.empty else 0.0
    balance_neto = total_ingresos - total_gastos

    c_f1, c_f2, c_f3 = st.columns(3)
    c_f1.metric("💵 Total Ingresado", f"${total_ingresos:,.0f}")
    c_f2.metric("🛒 Total Gastado", f"${total_gastos:,.0f}")
    c_f3.metric("📈 Balance Neto", f"${balance_neto:,.0f}", delta=f"${balance_neto:,.0f}")
    
    st.divider()

    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        st.markdown("#### 🛒 Registrar Gasto")
        with st.form("form_gastos", clear_on_submit=True):
            item = st.text_input("Insumo / Producto")
            cant_gasto = st.number_input("Cantidad", min_value=1, value=1)
            precio_uni = st.number_input("Costo Unitario ($)", min_value=0.0, step=1000.0)
            if st.form_submit_button("Guardar Gasto") and item:
                hoy = datetime.utcnow() - timedelta(hours=3)
                n_gasto = pd.DataFrame([{"Fecha_Obj": hoy, "Fecha": hoy.strftime("%d/%m/%Y"), "Item": item, "Cantidad": cant_gasto, "Precio_Unitario": precio_uni, "Total": cant_gasto * precio_uni}])
                
                if st.session_state.gastos.empty:
                    st.session_state.gastos = n_gasto
                else:
                    st.session_state.gastos = pd.concat([st.session_state.gastos, n_gasto], ignore_index=True)
                
                guardar_en_disco()
                st.rerun()
                
    with col_g2:
        st.markdown("#### 📋 Historial de Compras")
        if st.session_state.gastos.empty:
            st.info("No hay gastos registrados.")
        else:
            for idx_g, row_g in st.session_state.gastos.sort_values(by="Fecha_Obj", ascending=False).iterrows():
                with st.container():
                    st.markdown("<div style='background:#fff; padding:10px; border-radius:5px; border:1px solid #ddd; margin-bottom:5px;'>", unsafe_allow_html=True)
                    col_det1, col_det2, col_det3, col_det4 = st.columns([2, 4, 2, 1])
                    col_det1.write(f"📅 {row_g['Fecha']}")
                    col_det2.write(f"🛒 {row_g['Item']} (x{row_g['Cantidad']})")
                    col_det3.write(f"**${row_g['Total']:,.0f}**")
                    with col_det4:
                        with st.popover("🗑️"):
                            st.write("¿Eliminar este gasto?")
                            if st.button("Sí", key=f"del_g_{idx_g}"):
                                st.session_state.gastos = st.session_state.gastos.drop(idx_g)
                                guardar_en_disco()
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                    
