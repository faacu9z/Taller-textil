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
        "Precio_Total", "Sena", "Total_Pagado", "Saldo", "Historial_Pagos"
    ])

# Actualizar base de datos vieja si le faltan las columnas de historial financiero
nuevas_cols = {"Precio_Total": 0.0, "Sena": 0.0, "Total_Pagado": 0.0, "Saldo": 0.0, "Historial_Pagos": None}
for col, val in nuevas_cols.items():
    if col not in st.session_state.pedidos.columns:
        st.session_state.pedidos[col] = val

# Migrar pagos viejos al nuevo formato de historial sin perder datos
for idx_row in st.session_state.pedidos.index:
    if not isinstance(st.session_state.pedidos.at[idx_row, "Historial_Pagos"], list):
        sena_vieja = float(st.session_state.pedidos.at[idx_row, "Sena"]) if pd.notna(st.session_state.pedidos.at[idx_row, "Sena"]) else 0.0
        if sena_vieja > 0:
            f_obj = st.session_state.pedidos.at[idx_row, "Fecha_Obj"]
            hist_inicial = [{
                "Fecha_Obj": f_obj, "Fecha": f_obj.strftime("%d/%m/%Y"), "Hora": f_obj.strftime("%H:%M"),
                "Vendedor": st.session_state.pedidos.at[idx_row, "Vendedor"],
                "Concepto": "Seña Inicial", "Monto": sena_vieja, "Medio": "Efectivo"
            }]
            st.session_state.pedidos.at[idx_row, "Historial_Pagos"] = hist_inicial
            st.session_state.pedidos.at[idx_row, "Total_Pagado"] = sena_vieja
            st.session_state.pedidos.at[idx_row, "Saldo"] = float(st.session_state.pedidos.at[idx_row, "Precio_Total"]) - sena_vieja
        else:
            st.session_state.pedidos.at[idx_row, "Historial_Pagos"] = []
            st.session_state.pedidos.at[idx_row, "Total_Pagado"] = 0.0
            st.session_state.pedidos.at[idx_row, "Saldo"] = float(st.session_state.pedidos.at[idx_row, "Precio_Total"])

estados_posibles = [
    "1. Ingreso de pedido", "2. Diseño y confirmación de cliente", 
    "3. En plancha", "4. En costura", "5. Control de calidad", "6. Entregado"
]

tipos_prenda = [
    "camiseta sola", "camiseta + short", "sudadera", "sudadera + short", "chomba deportiva", 
    "conjunto de invierno", "short", "pechera", "bandera", "gorra", "campera"
]

medios_pago = ["Efectivo", "Transferencia", "Tarjeta", "QR"]

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
        st.write(f"👤 **Vendedor que tomó pedido:** {row['Vendedor']}")
    with col_det2:
        st.write(f"**Prenda:** {row['Prenda']} (x{row['Cantidad']})")
        st.write(f"🎨 **Diseño:** {row['Diseno']}")
    with col_det3:
        st.write(f"📅 **Fecha ingreso:** {row['Fecha']} - {row['Hora']}")
        nuevo_est_det = st.selectbox("Estado Actual", estados_posibles, index=estados_posibles.index(row["Estado"]), key="est_det_unico")
        if nuevo_est_det != row["Estado"]:
            st.session_state.pedidos.at[idx, "Estado"] = nuevo_est_det
            st.rerun()

    st.divider()

    # --- HISTORIAL FINANCIERO DEL PEDIDO ---
    st.markdown("### 💰 Finanzas y Pagos")
    
    # Métricas resumen
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Precio Total Acordado", f"${row['Precio_Total']:,.2f}")
    col_r2.metric("Total Pagado (Abonado)", f"${row['Total_Pagado']:,.2f}")
    col_r3.metric("Saldo Restante (Falta Pagar)", f"${row['Saldo']:,.2f}")

    # Tabla de Historial
    st.markdown("#### 📜 Archivo Histórico de Pagos")
    if isinstance(row['Historial_Pagos'], list) and len(row['Historial_Pagos']) > 0:
        df_historial = pd.DataFrame(row['Historial_Pagos']).drop(columns=["Fecha_Obj"])
        st.dataframe(df_historial, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no se registraron señas ni pagos para este pedido.")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if row['Saldo'] > 0:
            with st.expander("➕ Registrar Pago de Saldo (Cancelación)"):
                with st.form(f"form_pago_{idx}"):
                    st.write("Registrá el ingreso de dinero y actualizá el saldo.")
                    monto_a_pagar = st.number_input("Monto a Abonar ($)", min_value=0.0, max_value=float(row['Saldo']), value=float(row['Saldo']), step=1000.0)
                    medio_pago_saldo = st.selectbox("Medio de Pago", medios_pago)
                    
                    if st.form_submit_button("Confirmar Pago"):
                        if monto_a_pagar > 0:
                            ahora = datetime.utcnow() - timedelta(hours=3)
                            nuevo_pago = {
                                "Fecha_Obj": ahora,
                                "Fecha": ahora.strftime("%d/%m/%Y"),
                                "Hora": ahora.strftime("%H:%M"),
                                "Vendedor": st.session_state.vendedor_actual,
                                "Concepto": "Cancelación de Saldo",
                                "Monto": monto_a_pagar,
                                "Medio": medio_pago_saldo
                            }
                            
                            historial_actual = row['Historial_Pagos']
                            if not isinstance(historial_actual, list): historial_actual = []
                            historial_actual.append(nuevo_pago)
                            
                            nuevo_pagado = row['Total_Pagado'] + monto_a_pagar
                            
                            st.session_state.pedidos.at[idx, "Historial_Pagos"] = historial_actual
                            st.session_state.pedidos.at[idx, "Total_Pagado"] = nuevo_pagado
                            st.session_state.pedidos.at[idx, "Saldo"] = row['Precio_Total'] - nuevo_pagado
                            st.success("¡Pago registrado en el historial!")
                            st.rerun()
        else:
            st.success("✅ Este pedido se encuentra totalmente PAGADO.")

    with col_btn2:
        with st.expander("✏️ Modificar Precio Total del Pedido"):
            with st.form(f"form_precio_{idx}"):
                nuevo_precio = st.number_input("Nuevo Precio Total ($)", min_value=float(row['Total_Pagado']), value=float(row['Precio_Total']), step=1000.0)
                if st.form_submit_button("Actualizar Precio"):
                    st.session_state.pedidos.at[idx, "Precio_Total"] = nuevo_precio
                    st.session_state.pedidos.at[idx, "Saldo"] = nuevo_precio - row['Total_Pagado']
                    st.success("Precio actualizado.")
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
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            precio_tot = st.number_input("Precio Total ($)", min_value=0.0, step=1000.0)
        with col_p2:
            sena = st.number_input("Entrega / Seña Inicial ($)", min_value=0.0, step=1000.0)
            mp_sena = st.selectbox("Medio de Pago (Seña)", medios_pago)

        if st.form_submit_button("Guardar Pedido") and cliente:
            ahora = datetime.utcnow() - timedelta(hours=3)
            
            historial_inicial = []
            if sena > 0:
                historial_inicial.append({
                    "Fecha_Obj": ahora,
                    "Fecha": ahora.strftime("%d/%m/%Y"),
                    "Hora": ahora.strftime("%H:%M"),
                    "Vendedor": st.session_state.vendedor_actual,
                    "Concepto": "Seña",
                    "Monto": sena,
                    "Medio": mp_sena
                })

            nuevo_df = pd.DataFrame([{
                "ID_Base": len(st.session_state.pedidos) + 1,
                "Cliente": cliente, "Telefono": telefono, "Prenda": prenda, "Cantidad": cantidad,
                "Diseno": diseno, "ArchivoPC": archivo_pc.strip() or "S/N",
                "TablaTalles": pd.DataFrame([{"Nombre": "", "Talle": "", "Número": "", "Short": False}]),
                "Observaciones": "", "Imagen": None, "Estado": estados_posibles[0], "Vendedor": st.session_state.vendedor_actual,
                "Fecha_Obj": ahora, "Fecha": ahora.strftime("%d/%m/%Y"), "Hora": ahora.strftime("%H:%M"), "Anio": ahora.strftime("%Y"),
                "Precio_Total": precio_tot, "Sena": sena, "Total_Pagado": sena, "Saldo": precio_tot - sena,
                "Historial_Pagos": historial_inicial
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
                        st.markdown(f"<span style='color:{'#2E7D32' if row['Saldo']==0 else '#D32F2F'}'><b>💸 Falta: ${row['Saldo']:,.0f}</b></span>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 3: FINANZAS Y STOCK ---
with tab_finanzas:
    st.markdown("### 📊 Control de Finanzas y Stock")
    
    # Selector de período
    periodo = st.radio("Seleccione el período de análisis:", ["Semanal", "Mensual", "Anual", "Histórico Total"], horizontal=True)
    
    hoy = datetime.utcnow() - timedelta(hours=3)
    
    if periodo == "Semanal":
        inicio_periodo = hoy - timedelta(days=hoy.weekday())
        inicio_periodo = inicio_periodo.replace(hour=0, minute=0, second=0, microsecond=0)
        lbl_periodo = "de la Semana"
    elif periodo == "Mensual":
        inicio_periodo = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        lbl_periodo = "del Mes"
    elif periodo == "Anual":
        inicio_periodo = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        lbl_periodo = "del Año"
    else:
        inicio_periodo = datetime(2000, 1, 1) # Fecha antigua para incluir todo
        lbl_periodo = "Total"
    
    # 1. Calcular Ingresos reales leyendo el historial de pagos
    total_ingresos = 0.0
    for pagos_lista in st.session_state.pedidos["Historial_Pagos"]:
        if isinstance(pagos_lista, list):
            for pago in pagos_lista:
                if "Fecha_Obj" in pago and pago["Fecha_Obj"] >= inicio_periodo:
                    total_ingresos += float(pago["Monto"])
                    
    # 2. Calcular Gastos reales del período seleccionado
    gastos_periodo = st.session_state.gastos[st.session_state.gastos["Fecha_Obj"] >= inicio_periodo]
    total_gastos = gastos_periodo["Total"].sum() if not gastos_periodo.empty else 0.0
    
    balance_neto = total_ingresos - total_gastos

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1: st.markdown(f"<div class='metric-card'><h4>📈 Ingresos {lbl_periodo}</h4><h2>${total_ingresos:,.2f}</h2><p>Pagos y señas recibidas</p></div>", unsafe_allow_html=True)
    with col_m2: st.markdown(f"<div class='metric-card'><h4>📉 Gastos {lbl_periodo}</h4><h2 style='color:#D32F2F;'>${total_gastos:,.2f}</h2><p>Compras e insumos</p></div>", unsafe_allow_html=True)
    with col_m3: st.markdown(f"<div class='metric-card'><h4>⚖️ Balance {lbl_periodo}</h4><h2 style='color:{'#2E7D32' if balance_neto>=0 else '#D32F2F'};'>${balance_neto:,.2f}</h2><p>Ingresos - Gastos</p></div>", unsafe_allow_html=True)

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
        st.markdown(f"#### 📋 Historial de Compras ({periodo})")
        if gastos_periodo.empty:
            st.info(f"No hay gastos registrados en este período ({periodo.lower()}).")
        else:
            df_g_mostrar = gastos_periodo.copy().sort_values(by="Fecha_Obj", ascending=False).drop(columns=["Fecha_Obj"])
            st.dataframe(df_g_mostrar, use_container_width=True, hide_index=True)
