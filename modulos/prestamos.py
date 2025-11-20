import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import time

# ---------------------------------------------------
# 1. VERIFICAR GRUPO DEL USUARIO
# ---------------------------------------------------
def prestamos():
    if "id_grupo" not in st.session_state:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]

    st.markdown("<h2 style='text-align:center;'>💰 Módulo de Préstamos</h2>", unsafe_allow_html=True)

    mostrar_formulario_prestamo(id_grupo)
    mostrar_lista_prestamos(id_grupo)


# ---------------------------------------------------
# 2. FORMULARIO PARA CREAR UN PRÉSTAMO
# ---------------------------------------------------
def mostrar_formulario_prestamo(id_grupo):

    st.markdown("<h3>➕ Registrar nuevo préstamo</h3>", unsafe_allow_html=True)

    # Obtener miembros del grupo
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT M.id_miembro, M.nombre 
        FROM Miembros M
        JOIN Grupomiembros G ON G.id_miembro = M.id_miembro
        WHERE G.id_grupo = %s
    """, (id_grupo,))
    miembros = cursor.fetchall()
    con.close()

    if not miembros:
        st.info("Este grupo todavía no tiene miembros.")
        return

    # Seleccionar miembro
    opciones = {f"{m[1]} (ID {m[0]})": m[0] for m in miembros}
    miembro_seleccionado = st.selectbox("Seleccione una socia:", list(opciones.keys()))
    id_miembro = opciones[miembro_seleccionado]

    # Formulario del préstamo
    with st.form("form_prestamo"):
        proposito = st.text_input("Propósito del préstamo")
        monto = st.number_input("Monto solicitado", min_value=1.0, step=1.0)
        fecha_desembolso = st.date_input("Fecha de desembolso")
        fecha_venc = st.date_input("Fecha de vencimiento")
        firma = st.text_input("Firma (nombre quien autoriza)")
        enviar = st.form_submit_button("Registrar Préstamo")

    if enviar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()
            cursor.execute("""
                INSERT INTO prestamos (id_miembro, proposito, monto, fecha_desembolso, fecha_vencimiento, firma, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id_miembro, proposito, monto, fecha_desembolso, fecha_venc, firma, "activo"))
            con.commit()
            st.success("✔ Préstamo registrado correctamente")
            time.sleep(0.5)
            st.experimental_rerun()
        finally:
            cursor.close()
            con.close()


# ---------------------------------------------------
# 3. MOSTRAR LISTA DE PRÉSTAMOS ACTIVOS
# ---------------------------------------------------
def mostrar_lista_prestamos(id_grupo):

    st.markdown("<h3>📋 Préstamos del grupo</h3>", unsafe_allow_html=True)

    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT P.id_prestamo, M.nombre, P.monto, P.proposito, P.fecha_desembolso, P.estado
        FROM prestamos P
        JOIN Miembros M ON M.id_miembro = P.id_miembro
        JOIN Grupomiembros G ON G.id_miembro = M.id_miembro
        WHERE G.id_grupo = %s
        ORDER BY P.id_prestamo DESC
    """, (id_grupo,))
    prestamos = cursor.fetchall()
    con.close()

    if not prestamos:
        st.info("No hay préstamos registrados en este grupo.")
        return

    df = pd.DataFrame(prestamos, columns=["ID", "Socia", "Monto", "Propósito", "Desembolso", "Estado"])
    st.dataframe(df, use_container_width=True)

    # Selección de préstamo
    opciones = {f"Préstamo {row[0]} - {row[1]}": row[0] for row in prestamos}
    seleccionado = st.selectbox("Selecciona un préstamo para ver pagos:", list(opciones.keys()))
    id_prestamo = opciones[seleccionado]

    mostrar_pagos(id_prestamo)


# ---------------------------------------------------
# 4. MOSTRAR PAGOS DE UN PRÉSTAMO
# ---------------------------------------------------
def mostrar_pagos(id_prestamo):

    st.markdown("<h3>📄 Pagos del préstamo</h3>", unsafe_allow_html=True)

    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT numero_pago, fecha, capital, interes, estado
        FROM prestamo_pagos
        WHERE id_prestamo = %s
        ORDER BY numero_pago
    """, (id_prestamo,))
    pagos = cursor.fetchall()
    con.close()

    if pagos:
        df = pd.DataFrame(pagos, columns=["Pago #", "Fecha", "Capital", "Interés", "Estado"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Este préstamo aún no tiene pagos registrados.")

    st.warning("⚠ Módulo de pagos próximamente…")
