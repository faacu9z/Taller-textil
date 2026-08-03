import streamlit as st
import sqlite3
from datetime import datetime
from database import conectar

def registrar_pedido_ui():
    st.subheader("📝 Nuevo Pedido Rápido")
    
    with st.form("form_nuevo_pedido", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del Cliente*")
        with col2:
            telefono = st.text_input("Celular / WhatsApp (ej: 3704...)")
            
        st.divider()
        st.markdown("### 👕 Detalle de Prendas y Talles")
        st.info("Agregá los renglones necesarios según los talles y cantidades que te encargó el cliente.")

        # Usamos session_state para mantener la tabla dinámica de ítems
        if "items_pedido" not in st.session_state:
            st.session_state.items_pedido = [{"prenda": "Remera", "talle": "L", "cantidad": 1, "precio": 0.0}]

        def agregar_fila():
            st.session_state.items_pedido.append({"prenda": "Remera", "talle": "M", "cantidad": 1, "precio": 0.0})

        def quitar_fila(idx):
            if len(st.session_state.items_pedido) > 1:
                st.session_state.items_pedido.pop(idx)

        # Renderizar filas de prendas/talles
        for i, item in enumerate(st.session_state.items_pedido):
            c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 0.5])
            with c1:
                st.session_state.items_pedido[i]["prenda"] = st.text_input(f"Prenda {i+1}", value=item["prenda"], key=f"p_{i}")
            with c2:
                st.session_state.items_pedido[i]["talle"] = st.text_input(f"Talle {i+1}", value=item["talle"], key=f"t_{i}")
            with c3:
                st.session_state.items_pedido[i]["cantidad"] = st.number_input(f"Cant {i+1}", min_value=1, value=item["cantidad"], key=f"c_{i}")
            with c4:
                st.session_state.items_pedido[i]["precio"] = st.number_input(f"Precio U. {i+1}", min_value=0.0, value=item["precio"], step=100.0, key=f"pr_{i}")
            with c5:
                st.write("")
                if st.button("❌", key=f"del_{i}"):
                    quitar_fila(i)
                    st.rerun()

        if st.button("➕ Agregar otro talle/prenda"):
            agregar_fila()
            st.rerun()

        st.divider()
        c_pago1, c_pago2 = st.columns(2)
        with c_pago1:
            senia = st.number_input("Seña Abonada ($)", min_value=0.0, step=100.0)
        
        submitted = st.form_submit_button("Guardar Pedido 💾", use_container_width=True)
        
        if submitted:
            if not nombre.strip() or not telefono.strip():
                st.error("Por favor completa el nombre y teléfono del cliente.")
                return

            # Calcular total general
            total_general = sum(item["cantidad"] * item["precio"] for item in st.session_state.items_pedido)
            saldo_pendiente = total_general - senia
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

            conexion = conectar()
            cursor = conexion.cursor()
            try:
                # 1. Insertar cabecera del pedido
                cursor.execute(
                    """
                    INSERT INTO pedidos (nombre_cliente, telefono_cliente, fecha, estado, senia, saldo, total)
                    VALUES (?, ?, ?, 'Activo', ?, ?, ?)
                    """,
                    (nombre.strip(), telefono.strip(), fecha_actual, senia, saldo_pendiente, total_general)
                )
                pedido_id = cursor.lastrowid

                # 2. Insertar los detalles (talles, cantidades)
                for item in st.session_state.items_pedido:
                    cursor.execute(
                        """
                        INSERT INTO detalle_pedidos (pedido_id, prenda, talle, cantidad, precio_unitario)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (pedido_id, item["prenda"], item["talle"], item["cantidad"], item["precio"])
                    )

                conexion.commit()
                st.success("¡Pedido registrado con éxito!")
                st.session_state.items_pedido = [{"prenda": "Remera", "talle": "L", "cantidad": 1, "precio": 0.0}]
                st.rerun()
            except Exception as e:
                conexion.rollback()
                st.error(f"Error al guardar: {e}")
            finally:
                conexion.close()

def listar_pedidos():
    st.subheader("📦 Gestión de Pedidos Activos")
    
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre_cliente, telefono_cliente, fecha, estado, senia, saldo, total FROM pedidos ORDER BY id DESC")
    pedidos = cursor.fetchall()
    
    if not pedidos:
        st.info("No hay pedidos registrados todavía.")
        conexion.close()
        return

    for p in pedidos:
        p_id, cliente, tel, fecha, estado, senia, saldo, total = p
        
        # Buscar detalles de talles para este pedido
        cursor.execute("SELECT prenda, talle, cantidad, precio_unitario FROM detalle_pedidos WHERE pedido_id = ?", (p_id,))
        detalles = cursor.fetchall()

        with st.expander(f"Pedido #{p_id} - {cliente} ({estado}) — Total: ${total:,.0f}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"📅 **Fecha:** {fecha}")
                st.write(f"📱 **Teléfono:** {tel}")
            with c2:
                st.write(f"💵 **Seña:** ${senia:,.0f}")
                st.write(f"⏳ **Saldo Restante:** ${saldo:,.0f}")
            
            st.markdown("---")
            st.markdown("**Desglose de Talles y Prendas:**")
            for det in detalles:
                prenda, talle, cant, precio_u = det
                st.text(f"• {cant}x {prenda} (Talle: {talle}) — Unitario: ${precio_u:,.0f}")

            # Botones de acción rápida
            col_a, col_b, col_c = st.columns(3)
            
            # Enlace directo a WhatsApp
            with col_a:
                mensaje_wa = f"Hola {cliente}! Te escribimos del taller textil por tu pedido #{p_id}. El total es ${total:,.0f}, abonaste ${senia:,.0f} y te queda un saldo de ${saldo:,.0f}."
                link_wa = f"https://wa.me/549{tel.replace(' ', '')}?text={urllib_parse.quote(mensaje_wa)}"
                st.markdown(f"[💬 Enviar WhatsApp]({link_wa})", unsafe_allow_html=True)

            with col_b:
                if estado == 'Activo':
                    if st.button(f"Marcar Entregado #{p_id}", key=f"ent_{p_id}"):
                        cursor.execute("UPDATE pedidos SET estado = 'Entregado', saldo = 0 WHERE id = ?", (p_id,))
                        conexion.commit()
                        st.success("¡Pedido marcado como entregado!")
                        st.rerun()

            with col_c:
                if st.button(f"Eliminar #{p_id}", key=f"del_ped_{p_id}"):
                    cursor.execute("DELETE FROM pedidos WHERE id = ?", (p_id,))
                    conexion.commit()
                    st.warning("Pedido eliminado.")
                    st.rerun()
                    
    conexion.close()

import urllib.parse
