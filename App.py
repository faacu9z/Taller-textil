import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="Gestión de Taller Textil", page_icon="🧵", layout="wide")

# Estilos visuales minimalistas
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: 500; background-color: #111111; color: white; border: none; padding: 0.5rem 1rem; }
    .stButton>button:hover { background-color: #333333; color: white; }
    .card-pedido { background: white; padding: 15px 20px; border-radius: 10px; border: 1px solid #EAEAEA; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .alerta-roja { color: #D32F2F; font-weight: bold; background-color: #FFEBEE; padding: 2px 6px; border-radius: 4px; }
    .metric-card { background: white; padding: 20px; border-radius: 10px; border: 1px solid #EAEAEA; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS ---
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {"admin": "1234"}

if "vendedor_actual" not in st.session_state:
    st.session_state.vendedor_actual = None

if "pedido_seleccionado" not in st.session_state:
    st.session_state.pedido_seleccionado = None

if "gastos" not in st.session_state:
    st.session_state.gastos = pd.DataFrame(columns=["Fecha_Obj", "Fecha", "Item", "Cantidad", "Precio_Unitario", "Total"])

if "pedidos" not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        "ID_Base", "Cliente", "Telefono", "Prenda", "Cantidad", "Diseno", "ArchivoPC", "TablaTalles", 
        "Observaciones", "Imagen", "Estado", "Vendedor", "Fecha_Obj", "Fecha", "Hora", "Anio",
        "Precio_Total", "Sena", "Saldo", "Medio_Pago_Sena", "Medio_Pago_Saldo"
    ])
else:
    # Actualizar base de datos vieja si le faltan las nuevas columnas de finanzas
    nuevas_cols = {"Precio_Total": 0.0, "Sena": 0.0, "Saldo": 0.0, "Medio_Pago_Sena": "Efectivo", "Medio_Pago_Saldo": "A definir"}
    for col, val in nuevas_cols.items():
        if col not in st.session_state.pedidos.columns:
            st.session_state.pedidos[col] = val

estados_posibles = [
    "1. Ingreso de pedido", "2. Diseño y confirmación de cliente", 
    "3. En plancha", "4. En costura", "5. Control de calidad", "6. Entregado"
]

tipos_prenda = [
    "camiseta sola", "camiseta + short", "sudadera", "sudadera + short", "chomba deportiva", 
    "conjunto de invierno", "short", "pechera", "bandera", "gorra", "campera"
]

medios_pago = ["Efectivo", "Transferencia", "Tarjeta", "QR"]
medios_pago_saldo = ["A definir", "Efectivo", "Transferencia", "Tarjeta", "QR"]

# --- LOGIN ---
if st.session_state.vendedor_actual is None:
    st.markdown("<h2 style='text-align: center; color: #111;'>🧵 Taller Textil</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Inicie sesión para acceder al sistema</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrar Vendedor"])
        with tab1:
            user_ingreso = st.text_input("Usuario", key="login_user")
            pass_ingreso = st.text_input("Contraseña", type="password", key="login_pass")
            if st.button("Entrar", key="btn_login"):
                if user_ingreso in st.session_state.usuarios and st.session_state.usuarios[user_ingreso] == pass_ingreso:
                    st.session_state.vendedor_actual = user_ingreso
                    st.rerun()
                else:
                    st.error("Datos incorrectos.")
        with tab2:
            nuevo_user = st.text_input("Nuevo Usuario", key="reg_user")
            nuevo_pass = st.text_input("Nueva Contraseña", type="password", key="reg_pass")
            if st.button("Registrar", key="btn_reg"):
                if nuevo_user and nuevo_pass:
                    if nuevo_user in st.session_state.usuarios:
                        st.warning("El usuario ya existe.")
                    else:
                        st.session_state.usuarios[nuevo_user] = nuevo_pass
                        st.success("¡Registrado con éxito! Ya podés iniciar sesión.")
    st.stop()

# --- VISTA DETALLADA ---
if st.session_state.pedido_seleccionado is not None:
    idx = st.session_state.pedido_seleccionado
    if idx not in st.session_state.pedidos.index:
        st.session_state.pedido_seleccionado = None
        st.rerun()
        
    row = st.session_state.pedidos.loc[idx]
    id_formateado = f"#{row['ID_Base']:03d}-{row['ArchivoPC']}"

    if st.button("← Volver a la lista de pedidos"):
        st.session_state.pedido_seleccionado = None
        st.rerun()

    st.markdown(f"## 📂 Detalle del Pedido: {id_formateado}")
    
    col_det1, col_det2, col_det3 = st.columns(3)
    with col_det1:
        st.write(f"**Cliente:** {row['Cliente']}")
        st.write(f"📲 **WhatsApp:** {row['Telefono']}")
        st.write(f"👤 **Vendedor:** {row['Vendedor']}")
    with col_det2:
        st.write(f"**Prenda:** {row['Prenda']} (x{row['Cantidad']})")
        st.write(f"🎨 **Diseño:** {row['Diseno']}")
    with col_det3:
        st.write(f"📅 **Fecha:** {row['Fecha']} - {row['Hora']}")
        nuevo_est_det = st.selectbox("Estado Actual", estados_posibles, index=estados_posibles.index(row["Estado"]), key="est_det_unico")
        if nuevo_est_det != row["Estado"]:
            st.session_state.pedidos.at[idx, "Estado"] = nuevo_est_det
            st.rerun()

    st.divider()

    # Sección Financiera Editable
    st.markdown("### 💰 Finanzas del Pedido")
    with st.form(f"form_finanzas_{idx}"):
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            nuevo_precio = st.number_input("Precio Total ($)", value=float(row['Precio_Total']), step=1000.0)
        with col_f2:
            nueva_sena = st.number_input("Entrega / Seña ($)", value=float(row['Sena']), step=1000.0)
            nuevo_mp_sena = st.selectbox("Medio (Seña)", medios_pago, index=medios_pago.index(row['Medio_Pago_Sena']) if row['Medio_Pago_Sena'] in medios_pago else 0)
        with col_f3:
            st.metric("Falta Cancelar (Saldo)", f"${nuevo_precio - nueva_sena:,.2f}")
        with col_f4:
            nuevo_mp_saldo = st.selectbox("Medio esperado (Saldo)", medios_pago_saldo, index=medios_pago_saldo.index(row['Medio_Pago_Saldo']) if row['Medio_Pago_Saldo'] in medios_pago_saldo else 0)
        
        if st.form_submit_button("Actualizar Precios y Pagos"):
            st.session_state.pedidos.at[idx, "Precio_Total"] = nuevo_precio
            st.session_state.pedidos.at[idx, "Sena"] = nueva_sena
            st.session_state.pedidos.at[idx, "Saldo"] = nuevo_precio - nueva_sena
            st.session_state.pedidos.at[idx, "Medio_Pago_Sena"] = nuevo_mp_sena
            st.session_state.pedidos.at[idx, "Medio_Pago_Saldo"] = nuevo_mp_saldo
            st.success("Valores actualizados!")
            st.rerun()

    st.divider()

    st.markdown("### 📋 Talles y Nombres")
    if st.button("✅ Marcar TODOS con Short"):
        df_temp = row["TablaTalles"].copy()
        if not df_temp.empty:
            df_temp["Short"] = True
            st.session_state.pedidos.at[idx, "TablaTalles"] = df_temp
            st.rerun()

    with st.form(f"form_talles_{idx}"):
        df_actual = row["TablaTalles"].copy()
        if "Short" not in df_actual.columns: df_actual["Short"] = False
        df_actual["Short"] = df_actual["Short"].astype(bool)
        df_actual["Nombre"] = df_actual["Nombre"].astype(str)
        df_actual["Talle"] = df_actual["Talle"].astype(str)
        df_actual["Número"] = df_actual["Número"].astype(str)

        tabla_editada = st.data_editor(
            df_actual, num_rows="dynamic", use_container_width=True, key=f"ed_talles_{idx}",
            column_config={
                "Nombre": st.column_config.TextColumn("Nombre"), "Talle": st.column_config.TextColumn("Talle"),
                "Número": st.column_config.TextColumn("Número"), "Short": st.column_config.CheckboxColumn("Lleva Short", default=False)
            }
        )
        if st.form_submit_button("Guardar Cambios de Talles"):
            st.session_state.pedidos.at[idx, "TablaTalles"] = tabla_editada
            st.success("Guardado!")

    st.divider()
    st.markdown("### 📝 Observaciones")
    obs_actual = row["Observaciones"] if pd.notna(row["Observaciones"]) else ""
    nueva_obs = st.text_area("Notas:", value=obs_actual, key=f"obs_{idx}")
    if nueva_obs != obs_actual:
        st.session_state.pedidos.at[idx, "Observaciones"] = nueva_obs

    st.divider()
    st.markdown("### 🖼️ Imagen del Pedido")
    archivo_img = st.file_uploader("Subir imagen", type=["png", "jpg", "jpeg"], key=f"img_{idx}")
    if archivo_img:
        st.session_state.pedidos.at[idx, "Imagen"] = archivo_img
        st.success("Imagen cargada!")

    if "Imagen" in row and row["Imagen"] is not None:
        st.image(row["Imagen"], use_column_width=True)
        if st.button("🗑️ Eliminar Imagen"):
            st.session_state.pedidos.at[idx, "Imagen"] = None
            st.rerun()

    st.stop()

# --- BARRA SUPERIOR ---
col_top1, col_top2 = st.columns([6, 1])
with col_top1:
    st.title("🧵 Gestión de Producción")
with col_top2:
    st.write(f"👤 **{st.session_state.vendedor_actual}**")
    if st.button("Salir"):
        st.session_state.vendedor_actual = None
        st.rerun()

st.divider()

# --- PESTAÑAS PRINCIPALES ---
tab_nuevo, tab_lista, tab_finanzas = st.tabs(["➕ Nuevo Pedido", "📋 Pedidos en Curso", "📊 Finanzas y Stock"])

# --- PESTAÑA 1: NUEVO PEDIDO ---
with tab_nuevo:
    st.markdown("### Registrar Nuevo Pedido")
    with st.form("form_nuevo_pedido", clear_on_submit=True):
        st.markdown("#### 👤 Datos Básicos")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cliente = st.text_input("Nombre del Cliente")
            telefono = st.text_input("WhatsApp (ej: 549370...)")
            prenda = st.selectbox("Tipo de Prenda", tipos_prenda)
        with col_f2:
            cantidad = st.number_input("Cantidad", min_value=1, value=10)
            diseno = st.text_input("Diseño / Archivo")
            archivo_pc = st.text_input("Nro PC (Opcional)")
            
        st.markdown("#### 💰 Pagos")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            precio_tot = st.number_input("Precio Total ($)", min_value=0.0, step=1000.0)
        with col_p2:
            sena = st.number_input("Entrega / Seña ($)", min_value=0.0, step=1000.0)
            mp_sena = st.selectbox("Medio de Pago (Seña)", medios_pago)
        with col_p3:
            st.info("El saldo a cancelar se calcula automáticamente.")
            mp_saldo = st.selectbox("Medio a pagar el saldo", medios_pago_saldo)

        if st.form_submit_button("Guardar Pedido") and cliente:
            ahora = datetime.utcnow() - timedelta(hours=3)
            nuevo_df = pd.DataFrame([{
                "ID_Base": len(st.session_state.pedidos) + 1,
                "Cliente": cliente, "Telefono": telefono, "Prenda": prenda, "Cantidad": cantidad,
                "Diseno": diseno, "ArchivoPC": archivo_pc.strip() or "S/N",
                "TablaTalles": pd.DataFrame([{"Nombre": "", "Talle": "", "Número": "", "Short": False}]),
                "Observaciones": "", "Imagen": None, "Estado": estados_posibles[0], "Vendedor": st.session_state.vendedor_actual,
                "Fecha_Obj": ahora, "Fecha": ahora.strftime("%d/%m/%Y"), "Hora": ahora.strftime("%H:%M"), "Anio": ahora.strftime("%Y"),
                "Precio_Total": precio_tot, "Sena": sena, "Saldo": precio_tot - sena, 
                "Medio_Pago_Sena": mp_sena, "Medio_Pago_Saldo": mp_saldo
            }])
            st.session_state.pedidos = pd.concat([st.session_state.pedidos, nuevo_df], ignore_index=True)
            st.success("¡Pedido guardado!")

# --- PESTAÑA 2: LISTA DE PEDIDOS ---
with tab_lista:
    if st.session_state.pedidos.empty:
        st.info("No hay pedidos.")
    else:
        col_filt1, col_filt2 = st.columns(2)
        with col_filt1:
            filtro_est = st.selectbox("Filtrar:", ["Todos"] + estados_posibles)
        with col_filt2:
            busq = st.text_input("🔍 Buscar Pedido / PC:")
            
        df_most = st.session_state.pedidos.copy()
        if filtro_est != "Todos": df_most = df_most[df_most["Estado"] == filtro_est]
        if busq.strip():
            term = busq.strip().replace("#", "")
            df_most = df_most[df_most["ID_Base"].astype(str).str.contains(term, case=False) | df_most["ArchivoPC"].astype(str).str.contains(term, case=False)]

        ahora = datetime.utcnow() - timedelta(hours=3)
        if df_most.empty: st.warning("Sin resultados.")
        else:
            for idx, row in df_most.sort_values(by="Fecha_Obj").iterrows():
                alerta = (row["Estado"] == estados_posibles[1]) and ((ahora - row["Fecha_Obj"]).days >= 7)
                with st.container():
                    st.markdown('<div class="card-pedido">', unsafe_allow_html=True)
                    c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2, 2, 1.5])
                    with c1:
                        if st.button(f"📄 #{row['ID_Base']:03d}-{row['ArchivoPC']}", key=f"btn_p_{idx}"):
                            st.session_state.pedido_seleccionado = idx
                            st.rerun()
                        st.markdown(f'<span class="alerta-roja">📅 {row["Fecha"]}</span>' if alerta else f"<caption style='color:gray'>📅 {row['Fecha']}</caption>", unsafe_allow_html=True)
                    with c2:
                        st.write(f"**{row['Cliente']}**")
                        st.caption(f"📲 {row['Telefono']} | 👤 {row['Vendedor']}")
                    with c3:
                        st.write(f"**{row['Prenda']} (x{row['Cantidad']})**")
                        if alerta: st.markdown('<span class="alerta-roja">⚠️ >1 sem</span>', unsafe_allow_html=True)
                    with c4:
                        n_est = st.selectbox("Estado", estados_posibles, index=estados_posibles.index(row["Estado"]), key=f"est_{idx}", label_visibility="collapsed")
                        if n_est != row["Estado"]:
                            st.session_state.pedidos.at[idx, "Estado"] = n_est
                            st.rerun()
                    with c5:
                        st.caption(f"💰 Total: ${row['Precio_Total']:,.0f}")
                        st.caption(f"💸 Falta: ${row['Saldo']:,.0f}")
                    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 3: FINANZAS Y STOCK ---
with tab_finanzas:
    st.markdown("### 📊 Control y Stock Semanal")
    
    hoy = datetime.utcnow() - timedelta(hours=3)
    inicio_sem = hoy - timedelta(days=hoy.weekday())
    inicio_sem = inicio_sem.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Cálculos semanales
    pedidos_sem = st.session_state.pedidos[st.session_state.pedidos["Fecha_Obj"] >= inicio_sem]
    gastos_sem = st.session_state.gastos[st.session_state.gastos["Fecha_Obj"] >= inicio_sem]
    
    ingresos_senas = pedidos_sem["Sena"].sum() if not pedidos_sem.empty else 0
    # Asumimos ingreso del saldo si el pedido se marca como entregado esta semana (simplificación)
    ingresos_saldos = pedidos_sem[pedidos_sem["Estado"] == "6. Entregado"]["Saldo"].sum() if not pedidos_sem.empty else 0
    total_ingresos = ingresos_senas + ingresos_saldos
    total_gastos = gastos_sem["Total"].sum() if not gastos_sem.empty else 0
    balance_neto = total_ingresos - total_gastos

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1: st.markdown(f"<div class='metric-card'><h4>📈 Ingresos Semana</h4><h2>${total_ingresos:,.2f}</h2><p>Señas: ${ingresos_senas:,.2f} | Saldos: ${ingresos_saldos:,.2f}</p></div>", unsafe_allow_html=True)
    with col_m2: st.markdown(f"<div class='metric-card'><h4>📉 Gastos Semana</h4><h2 style='color:#D32F2F;'>${total_gastos:,.2f}</h2><p>Compras e insumos</p></div>", unsafe_allow_html=True)
    with col_m3: st.markdown(f"<div class='metric-card'><h4>⚖️ Balance</h4><h2 style='color:{'#2E7D32' if balance_neto>=0 else '#D32F2F'};'>${balance_neto:,.2f}</h2><p>Ingresos - Gastos</p></div>", unsafe_allow_html=True)

    st.divider()
    
    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        st.markdown("#### 🛒 Registrar Compra / Gasto")
        with st.form("form_gastos", clear_on_submit=True):
            item = st.text_input("Insumo / Producto")
            cant_gasto = st.number_input("Cantidad", min_value=1, value=1)
            precio_uni = st.number_input("Costo Unitario ($)", min_value=0.0, step=100.0)
            if st.form_submit_button("Guardar Gasto") and item:
                n_gasto = pd.DataFrame([{
                    "Fecha_Obj": hoy, "Fecha": hoy.strftime("%d/%m/%Y"),
                    "Item": item, "Cantidad": cant_gasto, "Precio_Unitario": precio_uni, "Total": cant_gasto * precio_uni
                }])
                st.session_state.gastos = pd.concat([st.session_state.gastos, n_gasto], ignore_index=True)
                st.rerun()
                
    with col_g2:
        st.markdown("#### 📋 Historial de Compras")
        if st.session_state.gastos.empty:
            st.info("No hay gastos registrados aún.")
        else:
            df_g_mostrar = st.session_state.gastos.copy().sort_values(by="Fecha_Obj", ascending=False).drop(columns=["Fecha_Obj"])
            st.dataframe(df_g_mostrar, use_container_width=True, hide_index=True)
