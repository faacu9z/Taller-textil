# Taller-textil
Aplicacion o programa para gestionar taller de textil y estado de prendas
import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Gestión de Taller Textil", page_icon="🧵", layout="wide")

# Estilos visuales rápidos para botones y tarjetas
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🧵 Control de Producción - Taller Textil")

# Simulación de Base de Datos en memoria (Se puede pasar a SQLite o Google Sheets después)
if "pedidos" not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        "ID", "Cliente", "Telefono", "Prenda", "Cantidad", "Diseno", "Estado", "Fecha"
    ])

estados_posibles = ["1. Pendiente / Ingresado", "2. Diseño", "3. Impresión y Plancha", "4. Costura", "5. Control de Calidad", "6. Listo / Entregado"]

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
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        nuevo_registro = pd.DataFrame([{
            "ID": nuevo_id,
            "Cliente": cliente,
            "Telefono": telefono,
            "Prenda": prenda,
            "Cantidad": cantidad,
            "Diseno": diseno,
            "Estado": estados_posibles[0],
            "Fecha": fecha_actual
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
                st.caption(row["Fecha"])
                
            with col2:
                st.write(f"**Cliente:** {row['Cliente']}")
                st.write(f"📲 {row['Telefono']}")
                
            with col3:
                st.write(f"**Prenda:** {row['Prenda']} (x{row['Cantidad']})")
                st.write(f"🎨 **Diseño:** {row['Diseno']}")
                
            with col4:
                # Selector para cambiar de estado rápidamente con un toque
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
