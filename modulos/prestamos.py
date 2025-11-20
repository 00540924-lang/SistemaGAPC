import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import datetime


# =====================================================
#   MÓDULO PRINCIPAL DE PRÉSTAMOS
# =====================================================
def prestamos_modulo():

    # --------------------------------------
    # Validar sesión y grupo
    # --------------------------------------
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]

    st.markdown("<h1 style='text-align:center;'>💲 Registro de Préstamos</h1>", unsafe_allow_html=True)

    # --------------------------------------
    # Obtener miembros del grupo
    # --------------------------------------
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT M.id_miembro, M.nombre, M.dui
        FROM Miembros M
        JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
    """, (id_grupo,))
    miembros = cursor.fetchall()
    con.close()

    if not miembros:
        st.warning("⚠ No hay miembros registrados en este grupo.")
        return

    miembros_dict = {f"{m[1]} - {m[2]}": m[0] for m in miembros}

    # =====================================================
    #   FORMULARIO: REGISTRAR NUEVO PRÉSTAMO
    # =====================================================
    with st.form("form_nuevo_prestamo"):
        st.subheader("📄 Datos del Préstamo")

        miembro_seleccionado = st.selectbox("Selecciona un miembro", list(miembros_dict.keys()))
        proposito = st.text_input("Propósito del préstamo")
        monto = st.number_input("Monto", min_value=0.01, step=0.01)
        fecha_desembolso = st.date_input("Fecha de desembolso", datetime.date.today())
        fecha_vencimiento = st.date_input("Fecha de vencimiento", datetime.date.today())
        firma = st.text_input("Firma del solicitante")
        estado = st.selectbox("Estado del préstamo", ["Pendiente", "Activo", "Finalizado"])

        enviar = st.form_submit_button("💾 Guardar Préstamo")

    if enviar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("""
                INSERT INTO prestamos (id_miembro, proposito, monto, fecha_desembolso, fecha_vencimiento, firma, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                miembros_dict[miembro_seleccionado],
                proposito,
                monto,
                fecha_desembolso,
                fecha_vencimiento,
                firma,
                estado
            ))

            con.commit()
            st.success("✅ Préstamo registrado correctamente")

        finally:
            cursor.close()
            con.close()

    # =====================================================
    #   MOSTRAR LISTA DE PRÉSTAMOS
    # =====================================================
    mostrar_lista_prestamos(id_grupo)



# =====================================================
#   TABLA DE PRÉSTAMOS
# =====================================================
def mostrar_lista_prestamos(id_grupo):

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("""
        SELECT P.id_prestamo, M.nombre, P.proposito, P.monto, 
               P.fecha_desembolso, P.fecha_vencimiento, P.estado
        FROM prestamos P
        JOIN Miembros M ON M.id_miembro = P.id_miembro
        JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
        ORDER BY P.id_prestamo DESC
    """, (id_grupo,))

    prestamos = cursor.fetchall()
    con.close()

    if not prestamos:
        st.info("No hay préstamos registrados en este grupo.")
        return

    df = pd.DataFrame(prestamos, columns=[
        "ID", "Miembro", "Propósito", "Monto", "Fecha Desembolso", "Fecha Vencimiento", "Estado"
    ])

    df.insert(0, "No.", range(1, len(df) + 1))

    st.subheader("📋 Préstamos registrados")
    st.dataframe(df, use_container_width=True)

    prestamo_opciones = {
        f"{row['Miembro']} - ${row['Monto']} (ID {row['ID']})": row["ID"]
        for _, row in df.iterrows()
    }

    prestamo_sel = st.selectbox("Selecciona un préstamo para registrar pagos:", list(prestamo_opciones.keys()))

    if prestamo_sel:
        mostrar_formulario_pagos(prestamo_opciones[prestamo_sel])



# =====================================================
#   FORMULARIO DE PAGOS CORREGIDO
# =====================================================
def mostrar_formulario_pagos(id_prestamo):

    st.markdown("<h3>💵 Registrar un pago</h3>", unsafe_allow_html=True)

    # Estados para limpiar después de guardar
    if "pago_form" not in st.session_state:
        st.session_state.pago_form = {
            "numero_pago": 1,
            "fecha_pago": datetime.date.today(),
            "capital": 0.01,
            "interes": 0.0,
            "estado": "Pendiente"
        }

    with st.form(f"form_pago_{id_prestamo}"):

        numero_pago = st.number_input("Número de pago", min_value=1, step=1,
                                      value=st.session_state.pago_form["numero_pago"])

        fecha_pago = st.date_input("Fecha del pago",
                                   value=st.session_state.pago_form["fecha_pago"])

        capital = st.number_input("Capital", min_value=0.01, step=0.01,
                                  value=st.session_state.pago_form["capital"])

        interes = st.number_input("Interés", min_value=0.00, step=0.01,
                                  value=st.session_state.pago_form["interes"])

        estado_pago = st.selectbox("Estado", ["Pendiente", "Pagado"],
                                   index=["Pendiente", "Pagado"].index(st.session_state.pago_form["estado"]))

        guardar = st.form_submit_button("💾 Registrar Pago")

    if guardar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("""
                INSERT INTO prestamo_pagos (id_prestamo, numero_pago, fecha, capital, interes, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                id_prestamo,
                numero_pago,
                fecha_pago,
                capital,
                interes,
                estado_pago
            ))

            con.commit()
            st.success("💰 Pago registrado correctamente")

            # Limpiar formulario para que aparezca limpio
            st.session_state.pago_form = {
                "numero_pago": 1,
                "fecha_pago": datetime.date.today(),
                "capital": 0.01,
                "interes": 0.0,
                "estado": "Pendiente"
            }

        finally:
            cursor.close()
            con.close()

