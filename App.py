import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Gestión de Taller Textil", page_icon="🧵", layout="wide")

# Estilos visuales
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS EN MEMORIA ---
if "usuarios" not in st.session_state:
    # Usuario por defecto para empezar (usuario: admin, pass: 1234)
    st.session_state.usuarios = {"admin": "1234"}

if "vendedor_actual" not in st.session_state:
    st.session_state.vendedor_actual = None

if "pedidos" not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        "ID", "Cliente", "Telefono", "Prenda", "Cantidad", "Diseno", "Estado", "Vendedor", "Fecha", "Hora", "Anio"
    ])

estados_posibles = [
    "1. Pendiente / Ingresado", 
    "2. Diseño", 
    "3. Impresión y Plancha", 
    "4. Costura", 
    "5. Control de Calidad", 
    "6. Listo / Entregado"
]

# --- SISTEMA DE LOGIN / AUTENTICACIÓN ---
if st.session_state.vendedor_actual is None:
    st.title("🔐 Acceso al Sistema - Taller Textil")
    
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrar Nuevo Vendedor"])
    
    with tab1:
        st.subheader("Login de Vendedor")
        user_ingreso = st.text_input("Usuario")
        pass_ingreso = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar al Sistema"):
            if user_ingreso in st.session_state.usuarios and st.session_state.usuarios[user_ingreso] == pass_ingreso:
                st.session_state.vendedor_actual = user_ingreso
                st.success(f"¡Bienvenido, {user_ingreso}!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
                
    with tab2:
        st.subheader("Crear Nuevo Vendedor")
        nuevo_user = st.text_input("Nuevo Usuario (Nombre)")
        nuevo_pass = st.text_input("Nueva Contraseña", type="password")
        
        if st.button("Registrar Vendedor"):
            if nuevo_user and nuevo_pass:
                if nuevo_user in st.session_state.usuarios:
                    st.warning("Ese usuario ya existe.")
                else:
                    st.session_state.usuarios[nuevo_user] = nuevo_pass
                    st.success(f"¡Vendedor '{nuevo_user}' registrado con éxito! Ya podés iniciar sesión.")
            else:
                st.error("Completá ambos campos.")
                
    st.stop() # Detiene la ejecución acá hasta que el usuario se loguee

# --- APLICACIÓN PRINCIPAL (Una vez logueado) ---
st.sidebar.write(f"👤 Conectado como: **{st.session_state.vendedor_actual}**")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.vendedor_actual = None
    st.rerun()

st.sidebar.divider()

st.title("🧵 Control de Producción - Taller Textil")

# --- MENÚ LATERAL: NUEVO PEDIDO ---
st.sidebar.header("➕ Nuevo Pedido")
with st.sidebar.form("form_pedido", clear_on_submit=True):
    cliente = st.text_input("Nombre del Cliente")
    telefono = st.text_input("Celular / WhatsApp (ej: 549370...)")
    prenda = st.selectbox("Tipo de Prenda", ["Remera", "Buzo", "Camiseta de Fútbol", "Pantalón", "Otro"])
    cantidad = st.number_input("Cantidad", min_value=1, value=10)
    diseno = st.text_input("Detalle del Diseño / Archivo")
    
    submitted = st.form_submit_button("Guardar Pedido")
    if submitted and cliente:
        nuevo_id = f"#{len(st.session_state.pedidos) + 1:03d}"
        ahora = datetime.now()
        fecha_str = ahora.strftime("%d/%m/%Y")
        hora_str = ahora.strftime("%H:%M")
        anio_str = ahora.strftime("%Y")
        
        nuevo_registro = pd.DataFrame([{
            "ID": nuevo_id,
            "Cliente": cliente,
            "Telefono": telefono,
            "Prenda": prenda,
            "Cantidad": cantidad,
            "Diseno": diseno,
            "Estado": estados_posibles[0],
            "Vendedor": st.session_state.vendedor_actual,
            "Fecha": fecha_str,
            "Hora": hora_str,
            "Anio": anio_str
        }])
        
        st.session_state.pedidos = pd.concat([st.session_state.pedidos, nuevo_registro], ignore_index=True)
        st.sidebar.success(f"¡Pedido {nuevo_id} creado con éxito!")

# --- PANTALLA PRINCIPAL: TABLERO DE PEDIDOS ---
st.subheader("📋 Estado de los Pedidos en Curso")

if st.session_state.pedidos.empty:
    st.info("No hay pedidos cargados todavía. Agregá uno desde el panel izquierdo.")
else:
    # Filtro por estado
    filtro_estado = st.selectbox("Filtrar por Estado:", ["Todos"] + estados_posibles)
    
    df_mostrar = st.session_state.pedidos
    if filtro_estado != "Todos":
        df_mostrar = df_mostrar[df_mostrar["Estado"] == filtro_estado]

    # Mostrar en tarjetas interactivas
    for index, row in df_mostrar.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
            
            with col1:
                st.markdown(f"### **{row['ID']}**")
                st.caption(f"📅 {row['Fecha']} - {row['Hora']} (Año {row['Anio']})")
                st.caption(f" vendedor: *{row['Vendedor']}*")
                
            with col2:
                st.write(f"**Cliente:** {row['Cliente']}")
                st.write(f"📲 {row['Telefono']}")
                
            with col3:
                st.write(f"**Prenda:** {row['Prenda']} (x{row['Cantidad']})")
                st.write(f"🎨 **Diseño:** {row['Diseno']}")
                
            with col4:
                # Selector para cambiar de estado rápidamente
                nuevo_estado = st.selectbox(
                    "Estado Actual", 
                    estados_posibles, 
                    index=estados_posibles.index(row["Estado"]),
                    key=f"estado_{row['ID']}"
                )
                if nuevo_estado != row["Estado"]:
                    st.session_state.pedidos.at[index, "Estado"] = nuevo_estado
                    st.rerun()
                
                # Botón de WhatsApp Web integrado
                if row["Telefono"]:
                    mensaje = f"Hola {row['Cliente']}! Te escribimos de la fábrica textil para avisarte que tu pedido {row['ID']} ({row['Cantidad']} {row['Prenda']}) se encuentra en estado: *{row['Estado']}*."
                    url_wa = f"https://wa.me/{row['Telefono']}?text={mensaje.replace(' ', '%20')}"
                    st.markdown(f"[💬 Enviar WhatsApp]({url_wa})", unsafe_allow_html=True)
                    
            st.divider()
