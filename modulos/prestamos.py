import streamlit as st
import mysql.connector
from datetime import date
from datetime import datetime

# ==========================================
# CONEXIÓN A BASE DE DATOS
# ==========================================
def get_connection():
    return mysql.connector.connect(
        host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
        user="uiazxdhtd3r8o7uv",
        password="uGjZ9MXWemv7vPsjOdA5",
        database="bzn5gsi7ken7lufcglbg"
    )

# ==========================================
# MÓDULO DE PRÉSTAMOS
# ==========================================
def prestamos_modulo():

    st.title("📄 Registro de Préstamos")

    # ==============================
    # Validar que existe un grupo
    # ==============================
    id_grupo = st.session_state.get("id_grupo", None)
    if not id_grupo:
        st.error("❌ No se detectó el grupo del usuario. Inicie sesión nuevamente.")
        st.stop()

    # ==============================
    # Cargar miembros del grupo
    # ==============================
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT Miembros.id, Miembros.nombre
            FROM Grupomiembros
            JOIN Miembros ON Grupomiembros.id_miembro = Miembros.id
            WHERE Grupomiembros.id_grupo = %s
        """, (id_grupo,))

        miembros = cursor.fetchall()

    except mysql.connector.Error as err:
        st.error(f"❌ Error al cargar miembros: {err}")
        conn.close()
        return

    if not miembros:
        st.warning("⚠ No hay miembros registrados en tu grupo.")
        conn.close()
        return

    miembros_dict = {m[1]: m[0] for m in miembros}  # nombre ➜ id

    # ======================================
    # FORMULARIO DE PRÉSTAMO
    # ======================================
    with st.form("form_prestamo"):
        st.subheader("🧾 Datos del Préstamo")

        nombre_miembro = st.selectbox("Seleccione un miembro:", list(miembros_dict.keys()))
        monto = st.number_input("Monto del préstamo:", min_value=1.0, step=1.0)
        fecha = st.date_input("Fecha del préstamo:", value=date.today())
        cantidad_pagos = st.number_input("Cantidad de pagos:", min_value=1, step=1)

        submitted = st.form_submit_button("💾 Guardar Préstamo")

    # ======================================
    # GUARDAR PRÉSTAMO
    # ======================================
    if submitted:

        id_miembro = miembros_dict[nombre_miembro]

        cursor.execute("""
            INSERT INTO prestamos (id_miembro, monto, fecha, cantidad_pagos)
            VALUES (%s, %s, %s, %s)
        """, (id_miembro, monto, fecha, cantidad_pagos))

        conn.commit()

        st.success("✅ Préstamo registrado con éxito.")

    # ======================================
    # PLAN DE PAGOS
    # ======================================
    st.subheader("📅 Plan de Pagos")

    if "pagos" not in st.session_state:
        st.session_state.pagos = 1

    col_a, col_b = st.columns(2)

    if col_a.button("➕ Agregar pago"):
        st.session_state.pagos += 1

    if col_b.button("➖ Quitar pago") and st.session_state.pagos > 1:
        st.session_state.pagos -= 1

    st.write("### Tabla de Pagos")

    for i in range(st.session_state.pagos):
        c1, c2 = st.columns(2)
        c1.date_input(f"Fecha pago {i+1}", key=f"fecha_pago_{i}")
        c2.number_input(f"Monto pago {i+1}", min_value=0.0, key=f"monto_pago_{i}")

    conn.close()
