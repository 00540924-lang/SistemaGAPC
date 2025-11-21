import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import time

def prestamos_modulo():

    st.header("Gestión de Préstamos")

    # ======================================
    # VALIDAR SESIÓN Y GRUPO
    # ======================================
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]

    # ======================================
    # CONEXIÓN A BD
    # ======================================
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # ======================================
    # OBTENER INTERÉS DESDE TABLA REGLAMENTO
    # ======================================
    cursor.execute("SELECT interes_aplicado FROM reglamento WHERE id_grupo = %s", (id_grupo,))
    reglamento = cursor.fetchone()

    interes_por_10 = reglamento[0] if reglamento else 0

    # Campo NO editable colocado donde estaba FIRMA
    st.subheader("Interés del Reglamento")
    interes_no_editable = st.number_input(
        "Interés aplicado por cada $10 (%)",
        value=float(interes_por_10),
        disabled=True
    )

    # ======================================
    # SELECCIONAR USUARIO
    # ======================================
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id_grupo = %s", (id_grupo,))
    usuarios = cursor.fetchall()

    usuarios_dict = {u[1]: u[0] for u in usuarios}
    nombre_usuario = st.selectbox("Seleccionar solicitante", list(usuarios_dict.keys()))
    id_usuario = usuarios_dict[nombre_usuario]

    # ======================================
    # INGRESAR MONTO A PRESTAR
    # ======================================
    monto = st.number_input("Monto a prestar ($)", min_value=1.0, step=1.0)

    # Cálculo del interés basado en el reglamento
    # Fórmula:
    #   interés = (monto / 10) * interes_por_10
    interes_calculado = (monto / 10) * interes_por_10

    total_a_pagar = monto + interes_calculado

    # ======================================
    # MOSTRAR CÁLCULO EN TIEMPO REAL
    # ======================================
    st.write(f"📌 **Interés generado:** ${interes_calculado:.2f}")
    st.write(f"💰 **Total a pagar:** ${total_a_pagar:.2f}")

    # ======================================
    # GUARDAR PRÉSTAMO
    # ======================================
    if st.button("Registrar Préstamo"):
        cursor.execute(
            """
            INSERT INTO prestamo_pagos (id_usuario, monto_prestamo, interes, total_pagar, id_grupo)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (id_usuario, monto, interes_calculado, total_a_pagar, id_grupo)
        )

        conexion.commit()
        st.success("Préstamo registrado correctamente.")
        time.sleep(1)
        st.experimental_rerun()

    st.subheader("Préstamos Registrados")

    cursor.execute(
        """
        SELECT u.nombre, p.monto_prestamo, p.interes, p.total_pagar
        FROM prestamo_pagos p
        JOIN usuarios u ON p.id_usuario = u.id
        WHERE p.id_grupo = %s
        ORDER BY p.id DESC
        """,
        (id_grupo,)
    )

    registros = cursor.fetchall()

    df = pd.DataFrame(registros, columns=["Usuario", "Monto Prestado", "Interés", "Total a Pagar"])

    st.dataframe(df)

    cursor.close()
    conexion.close()

