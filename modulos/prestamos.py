import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

def prestamos():
    # ================================
    # Validar sesión y grupo
    # ================================
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo desconocido")

    st.markdown(f"<h2 style='text-align:center;'>💰 Préstamos - {nombre_grupo}</h2>", unsafe_allow_html=True)

    # ================================
    # Obtener miembros del grupo
    # ================================
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT M.id_miembro, M.nombre 
            FROM Miembros M
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY M.nombre ASC
        """, (id_grupo,))

        miembros = cursor.fetchall()

        if not miembros:
            st.warning("No hay miembros registrados en este grupo.")
            return

        # Convertir a diccionario para mostrarlo en selectbox
        miembros_dict = {nombre: mid for mid, nombre in miembros}

        miembro_seleccionado = st.selectbox(
            "Selecciona una socia para generar un préstamo:",
            options=list(miembros_dict.keys())
        )

        id_miembro = miembros_dict[miembro_seleccionado]

    finally:
        cursor.close()
        con.close()

    # ================================
    # Formulario de préstamo
    # ================================
    st.markdown("<h3>📄 Formulario de préstamo</h3>", unsafe_allow_html=True)

    with st.form("form_prestamo"):
        fecha_desembolso = st.date_input("Fecha de desembolso")
        fecha_vencimiento = st.date_input("Fecha de vencimiento")
        proposito = st.text_input("Propósito")
        cantidad = st.number_input("Cantidad", min_value=1.0, step=0.5)
        
        enviar = st.form_submit_button("Guardar préstamo")

    if enviar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("""
                INSERT INTO Prestamos (id_miembro, fecha_desembolso, fecha_vencimiento, proposito, cantidad)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_miembro, fecha_desembolso, fecha_vencimiento, proposito, cantidad))

            con.commit()

            st.success("✔️ Préstamo registrado exitosamente")

        finally:
            cursor.close()
            con.close()
