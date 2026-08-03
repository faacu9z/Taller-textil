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
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS ---
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {"admin": "1234"}

if "vendedor_actual" not in st.session_state:
    st.session_state.vendedor_actual = None

if "pedidos" not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        "ID", "Cliente", "Telefono", "Prenda", "Cantidad", "Diseno", "Estado", "Vendedor", "Fecha_Obj", "Fecha", "Hora", "Anio"
    ])

# Nuevas etapas solicitadas
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
            
        submitted = st.form_submit_button("Guardar y Registrar Pedido")
        if submitted and cliente:
            nuevo_id = f"#{len(st.session_state.pedidos) + 1:03d}"
            
            ahora_argentina = datetime.utcnow() - timedelta(hours=3)
            fecha_str = ahora_argentina.strftime("%d/%m/%Y")
            hora_str = ahora_argentina.strftime("%H:%M")
            anio_str = ahora_argentina.strftime("%Y")
            
            nuevo_registro = pd.DataFrame([{
                "ID": nuevo_id,
                "Cliente": cliente,
                "Telefono": telefono,
                "Prenda": prenda,
                "Cantidad": cantidad,
                "Diseno": diseno,
                "Estado": estados_posibles[0],
                "Vendedor": st.session_state.vendedor_actual,
                "Fecha_Obj": ahora_argentina,
                "Fecha": fecha_str,
                "Hora": hora_str,
                "Anio": anio_str
            }])
            
            st.session_state.pedidos = pd.concat([st.session_state.pedidos, nuevo_registro], ignore_index=True)
            st.success(f"¡Pedido {nuevo_id} guardado con éxito!")

# --- PESTAÑA 2: PEDIDOS INGRESADOS (ORDENADOS MÁS VIEJOS PRIMERO) ---
with tab_lista:
    st.markdown("### Lista de Pedidos")
    
    if st.session_state.pedidos.empty:
        st.info("No hay pedidos cargados todavía.")
    else:
        filtro_estado = st.selectbox("Filtrar por Etapa:", ["Todos"] + estados_posibles)
        
        df_mostrar = st.session_state.pedidos.copy()
        if filtro_estado != "Todos":
            df_mostrar = df_mostrar[df_mostrar["Estado"] == filtro_estado]

        # Ordenar: Más viejos primero (ascendente por fecha de creación)
        if not df_mostrar.empty:
            df_mostrar = df_mostrar.sort_values(by="Fecha_Obj", ascending=True)

        ahora_actual = datetime.utcnow() - timedelta(hours=3)

        for index, row in df_mostrar.iterrows():
            # Control de alerta de 1 semana en etapa de Diseño
            alerta_tiempo = False
            if row["Estado"] == "2. Diseño y confirmación de cliente":
                diferencia = ahora_actual - row["Fecha_Obj"]
                if diferencia.days >= 7:
                    alerta_tiempo = True

            with st.container():
                st.markdown('<div class="card-pedido">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
                
                with col1:
                    st.markdown(f"#### **{row['ID']}**")
                    if alerta_tiempo:
                        st.markdown(f'<span class="alerta-roja">📅 {row["Fecha"]} - {row["Hora"]}</span>', unsafe_allow_html=True)
                    else:
                        st.caption(f"📅 {row['Fecha']} - {row['Hora']}")
                    st.caption(f"Vendedor: {row['Vendedor']}")
                    
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
                        key=f"estado_{row['ID']}"
                    )
                    if nuevo_estado != row["Estado"]:
                        st.session_state.pedidos.at[index, "Estado"] = nuevo_estado
                        st.rerun()
                    
                    if row["Telefono"]:
                        mensaje = f"Hola {row['Cliente']}! Te escribimos de la fábrica textil para avisarte que tu pedido {row['ID']} ({row['Cantidad']} {row['Prenda']}) se encuentra en la etapa: *{row['Estado']}*."
                        url_wa = f"https://wa.me/{row['Telefono']}?text={mensaje.replace(' ', '%20')}"
                        st.markdown(f"[💬 Enviar WhatsApp]({url_wa})", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
