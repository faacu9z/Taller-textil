import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuración de la página con diseño limpio
st.set_page_config(page_title="Gestión de Taller Textil", page_icon="🧵", layout="wide")

# Estilos visuales minimalistas y modernos
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: 500; background-color: #111111; color: white; border: none; padding: 0.5rem 1rem; }
    .stButton>button:hover { background-color: #333333; color: white; }
    .card-pedido { background: white; padding: 20px; border-radius: 10px; border: 1px solid #EAEAEA; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .alerta-roja { color: #D32F2F; font-weight: bold; background-color: #FFEBEE; padding: 2px 6px; border-radius: 4px; }
    .modal-detalle { background: #FFFFFF; padding: 25px; border-radius: 12px; border: 1px solid #E0E0E0; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS ---
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {"admin": "1234"}

if "vendedor_actual" not in st.session_state:
    st.session_state.vendedor_actual = None

if "pedidos" not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        "ID_Base", "Cliente", "Telefono", "Prenda", "Cantidad", "Diseno", "ArchivoPC", "TablaTalles", "Estado", "Vendedor", "Fecha_Obj", "Fecha", "Hora", "Anio"
    ])

estados_posibles = [
    "1. Ingreso de pedido", 
    "2. Diseño y confirmación de cliente", 
    "3. En plancha", 
    "4. En costura", 
    "5. Control de calidad", 
    "6. Entregado"
]

# --- SISTEMA DE LOGIN / AUTENTICACIÓN ---
if st.session_state.vendedor_actual is None:
    st.markdown("<h2 style='text-align: center; color: #111;'>🧵 Taller Textil</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Inicie sesión para acceder al sistema</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrar Vendedor"])
        
        with tab1:
            user_ingreso = st.text_input("Usuario")
            pass_ingreso = st.text_input("Contraseña", type="password")
            if st.button("Entrar"):
                if user_ingreso in st.session_state.usuarios and st.session_state.usuarios[user_ingreso] == pass_ingreso:
                    st.session_state.vendedor_actual = user_ingreso
                    st.rerun()
                else:
                    st.error("Datos incorrectos.")
                    
        with tab2:
            nuevo_user = st.text_input("Nuevo Usuario")
            nuevo_pass = st.text_input("Nueva Contraseña", type="password")
            if st.button("Registrar"):
                if nuevo_user and nuevo_pass:
                    if nuevo_user in st.session_state.usuarios:
                        st.warning("El usuario ya existe.")
                    else:
                        st.session_state.usuarios[nuevo_user] = nuevo_pass
                        st.success("¡Registrado con éxito! Ya podés iniciar sesión.")
                else:
                    st.error("Completá los campos.")
    st.stop()

# --- BARRA SUPERIOR DE USUARIO ---
col_top1, col_top2 = st.columns([6, 1])
with col_top1:
    st.title("🧵 Gestión de Producción")
with col_top2:
    st.write(f"👤 **{st.session_state.vendedor_actual}**")
    if st.button("Salir"):
        st.session_state.vendedor_actual = None
        st.rerun()

st.divider()

# --- DIVISIÓN EN 2 PESTAÑAS PRINCIPALES ---
tab_nuevo, tab_lista = st.tabs(["➕ Nuevo Pedido", "📋 Pedidos en Curso"])

# --- PESTAÑA 1: NUEVO PEDIDO ---
with tab_nuevo:
    st.markdown("### Registrar Nuevo Pedido")
    with st.form("form_pedido_principal", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cliente = st.text_input("Nombre del Cliente")
            telefono = st.text_input("Celular / WhatsApp (ej: 549370...)")
            prenda = st.selectbox("Tipo de Prenda", ["Remera", "Buzo", "Camiseta de Fútbol", "Pantalón", "Otro"])
        with col_f2:
            cantidad = st.number_input("Cantidad", min_value=1, value=10)
            diseno = st.text_input("Detalle del Diseño / Archivo")
            archivo_pc = st.text_input("Nro de Archivo en PC (Opcional)", value="")
            
        submitted = st.form_submit_button("Guardar y Registrar Pedido")
        if submitted and cliente:
            secuencial = len(st.session_state.pedidos) + 1
            num_pc_str = archivo_pc.strip() if archivo_pc.strip() else "S/N"
            
            ahora_argentina = datetime.utcnow() - timedelta(hours=3)
            fecha_str = ahora_argentina.strftime("%d/%m/%Y")
            hora_str = ahora_argentina.strftime("%H:%M")
            anio_str = ahora_argentina.strftime("%Y")
            
            # DataFrame inicial con columnas Nombre, Talle, Número y Short (booleano)
            df_vacio = pd.DataFrame(
                [{"Nombre": "", "Talle": "", "Número": "", "Short": False}],
                columns=["Nombre", "Talle", "Número", "Short"]
            )
            
            nuevo_registro = pd.DataFrame([{
                "ID_Base": secuencial,
                "Cliente": cliente,
                "Telefono": telefono,
                "Prenda": prenda,
                "Cantidad": cantidad,
                "Diseno": diseno,
                "ArchivoPC": num_pc_str,
                "TablaTalles": df_vacio,
                "Estado": estados_posibles[0],
                "Vendedor": st.session_state.vendedor_actual,
                "Fecha_Obj": ahora_argentina,
                "Fecha": fecha_str,
                "Hora": hora_str,
                "Anio": anio_str
            }])
            
            st.session_state.pedidos = pd.concat([st.session_state.pedidos, nuevo_registro], ignore_index=True)
            st.success(f"¡Pedido guardado con éxito! Ya podés ver los detalles en la pestaña 'Pedidos en Curso'.")

# --- PESTAÑA 2: PEDIDOS INGRESADOS ---
with tab_lista:
    st.markdown("### Lista de Pedidos")
    
    if st.session_state.pedidos.empty:
        st.info("No hay pedidos cargados todavía.")
    else:
        filtro_estado = st.selectbox("Filtrar por Etapa:", ["Todos"] + estados_posibles)
        
        df_mostrar = st.session_state.pedidos.copy()
        if filtro_estado != "Todos":
            df_mostrar = df_mostrar[df_mostrar["Estado"] == filtro_estado]

        if not df_mostrar.empty:
            df_mostrar = df_mostrar.sort_values(by="Fecha_Obj", ascending=True)

        ahora_actual = datetime.utcnow() - timedelta(hours=3)

        for index, row in df_mostrar.iterrows():
            alerta_tiempo = False
            if row["Estado"] == "2. Diseño y confirmación de cliente":
                diferencia = ahora_actual - row["Fecha_Obj"]
                if diferencia.days >= 7:
                    alerta_tiempo = True

            id_formateado = f"#{row['ID_Base']:03d}-{row['ArchivoPC']}"

            with st.container():
                st.markdown('<div class="card-pedido">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns([1.5, 2, 2, 2])
                
                with col1:
                    st.markdown(f"#### **{id_formateado}**")
                    if alerta_tiempo:
                        st.markdown(f'<span class="alerta-roja">📅 {row["Fecha"]} - {row["Hora"]}</span>', unsafe_allow_html=True)
                    else:
                        st.caption(f"📅 {row['Fecha']} - {row['Hora']}")
                    st.caption(f"Vendedor: {row['Vendedor']}")
                    
                    # Modificar número de PC de forma independiente
                    nuevo_pc = st.text_input("Nro Archivo PC", value=row["ArchivoPC"], key=f"pc_{index}")
                    if nuevo_pc != row["ArchivoPC"]:
                        st.session_state.pedidos.at[index, "ArchivoPC"] = nuevo_pc.strip() if nuevo_pc.strip() else "S/N"
                        st.rerun()
                    
                with col2:
                    st.write(f"**Cliente:** {row['Cliente']}")
                    st.write(f"📲 {row['Telefono']}")
                    
                with col3:
                    st.write(f"**Prenda:** {row['Prenda']} (x{row['Cantidad']})")
                    st.write(f"🎨 **Diseño:** {row['Diseno']}")
                    if alerta_tiempo:
                        st.markdown('<span class="alerta-roja">⚠️ Más de 1 semana en diseño</span>', unsafe_allow_html=True)
                    
                with col4:
                    nuevo_estado = st.selectbox(
                        "Cambiar Etapa", 
                        estados_posibles, 
                        index=estados_posibles.index(row["Estado"]),
                        key=f"estado_{row['ID_Base']}"
                    )
                    if nuevo_estado != row["Estado"]:
                        st.session_state.pedidos.at[index, "Estado"] = nuevo_estado
                        st.rerun()
                    
                    if row["Telefono"]:
                        mensaje = f"Hola {row['Cliente']}! Te escribimos de la fábrica textil para avisarte que tu pedido {id_formateado} ({row['Cantidad']} {row['Prenda']}) se encuentra en la etapa: *{row['Estado']}*."
                        url_wa = f"https://wa.me/{row['Telefono']}?text={mensaje.replace(' ', '%20')}"
                        st.markdown(f"[💬 Enviar WhatsApp]({url_wa})", unsafe_allow_html=True)

                st.markdown('---')

                # --- SECCIÓN INTERNA DEL PEDIDO (ABIERTA DIRECTAMENTE EN LA TARJETA) ---
                st.markdown(f"### 📂 Detalle del Pedido: {id_formateado}")
                st.write(f"**Descripción:** Pedido de {row['Cantidad']} {row['Prenda']} para el cliente **{row['Cliente']}**. Estado actual: *{row['Estado']}*.")
                
                st.markdown("---")
                st.write("#### 📋 Listado de Nombres, Talles, Números y Shorts")
                
                # Opción para marcar que TODOS llevan short
                col_btn_short, _ = st.columns([2, 4])
                with col_btn_short:
                    if st.button("✅ Marcar que TODOS llevan Short", key=f"btn_todos_short_{index}"):
                        df_temp = row["TablaTalles"].copy()
                        if not df_temp.empty:
                            df_temp["Short"] = True
                            st.session_state.pedidos.at[index, "TablaTalles"] = df_temp
                            st.success("¡Se marcó que todos llevan short!")
                            st.rerun()

                # Editor de datos estable con configuración de tipos explícita para evitar pérdida de foco/valores
                df_actual = row["TablaTalles"].copy()
                
                # Asegurar tipos de datos correctos en el DataFrame
                if "Short" not in df_actual.columns:
                    df_actual["Short"] = False
                df_actual["Short"] = df_actual["Short"].astype(bool)
                df_actual["Nombre"] = df_actual["Nombre"].astype(str)
                df_actual["Talle"] = df_actual["Talle"].astype(str)
                df_actual["Número"] = df_actual["Número"].astype(str)

                tabla_editada = st.data_editor(
                    df_actual,
                    num_rows="dynamic",
                    key=f"editor_talles_{index}",
                    use_container_width=True,
                    column_config={
                        "Nombre": st.column_config.TextColumn("Nombre"),
                        "Talle": st.column_config.TextColumn("Talle"),
                        "Número": st.column_config.TextColumn("Número"),
                        "Short": st.column_config.CheckboxColumn("Lleva Short", default=False)
                    }
                )

                # Guardado automático e inmediato al interactuar con la tabla
                if not tabla_editada.equals(df_actual):
                    st.session_state.pedidos.at[index, "TablaTalles"] = tabla_editada

                st.markdown('</div>', unsafe_allow_html=True)
