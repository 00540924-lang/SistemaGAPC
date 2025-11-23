import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import datetime
import time

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

    # TÍTULO
    st.markdown("<h1 style='text-align:center;'>💲 Registro de Préstamos</h1>", unsafe_allow_html=True)

    # --------------------------------------
    # Obtener nombre del grupo
    # --------------------------------------
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("SELECT Nombre_grupo FROM Grupos WHERE id_grupo = %s", (id_grupo,))
    grupo = cursor.fetchone()
    con.close()

    nombre_grupo = grupo[0] if grupo else "Grupo desconocido"

    # Mostrar nombre debajo del título
    st.markdown(
        f"<h3 style='text-align:center; color:#555;'>Grupo: {nombre_grupo}</h3>",
        unsafe_allow_html=True
    )

    # --------------------------------------
    # Obtener valores del reglamento
    # --------------------------------------
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT interes_por_10
        FROM Reglamento
        WHERE id_grupo = %s
        LIMIT 1
    """, (id_grupo,))
    reglamento = cursor.fetchone()
    con.close()

    interes_por_10 = float(reglamento[0]) if reglamento else 0.0

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

    miembros_dict = {m[1]: m[0] for m in miembros}

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

        # ⚠️ CAMPO DE INTERÉS — SOLO LECTURA
        st.number_input(
            "Interés aplicado por cada $10 (%)",
            value=interes_por_10,
            step=0.01,
            disabled=True
        )

        estado = st.selectbox("Estado del préstamo", ["Pendiente", "Activo", "Finalizado"])

        enviar = st.form_submit_button("💾 Guardar Préstamo")

    # BOTÓN REGRESAR - FUERA DEL FORMULARIO
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
    st.write("---")

    if enviar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            # Calcular el interés total
            interes_total = (monto / 10) * interes_por_10

            # INSERT CORREGIDO con los nombres correctos
            cursor.execute("""
                INSERT INTO prestamos (id_miembro, proposito, monto, fecha_desembolso, fecha_vencimiento, estado, interes_total)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                miembros_dict[miembro_seleccionado],
                proposito,
                monto,
                fecha_desembolso,
                fecha_vencimiento,
                estado.lower(),
                interes_total
            ))

            con.commit()
            st.success("✅ Préstamo registrado correctamente")
            st.info(f"💰 Interés total calculado: ${interes_total:,.2f}")
            time.sleep(1.5)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar préstamo: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'con' in locals() and con.is_connected():
                con.close()

    mostrar_lista_prestamos(id_grupo)


# =====================================================
#   TABLA DE PRÉSTAMOS
# =====================================================
def mostrar_lista_prestamos(id_grupo):

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("""
        SELECT P.id_prestamo, M.nombre, P.proposito, P.monto,
               P.fecha_desembolso, P.fecha_vencimiento, P.estado, P.interes_total
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
        "ID", "Miembro", "Propósito", "Monto", "Fecha Desembolso", "Fecha Vencimiento", "Estado", "Interés Total"
    ])

    st.subheader("📋 Préstamos registrados")
    st.dataframe(df, use_container_width=True)

    # MODIFICACIÓN: Mostrar nombre + monto total (monto + interés) sin "ID"
    prestamo_opciones = {}
    for _, row in df.iterrows():
        monto_total = row['Monto'] + row['Interés Total']
        texto_opcion = f"{row['Miembro']} - Total a pagar: ${monto_total:,.2f} (Capital: ${row['Monto']:,.2f} + Interés: ${row['Interés Total']:,.2f})"
        prestamo_opciones[texto_opcion] = row["ID"]

    prestamo_sel = st.selectbox("Selecciona un préstamo para registrar pagos:", list(prestamo_opciones.keys()))

    if prestamo_sel:
        mostrar_formulario_pagos(prestamo_opciones[prestamo_sel])


# =====================================================
#   FORMULARIO DE PAGOS
# =====================================================
def mostrar_formulario_pagos(id_prestamo):

    st.markdown("<h3>💵 Registrar un pago</h3>", unsafe_allow_html=True)

    # Obtener interes_por_10 desde reglamento
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT interes_por_10
        FROM Reglamento
        WHERE id_grupo = %s
        LIMIT 1
    """, (st.session_state["id_grupo"],))
    reglamento = cursor.fetchone()
    con.close()

    interes_por_10 = float(reglamento[0]) if reglamento else 0.0

    with st.form(f"form_pago_{id_prestamo}"):

        numero_pago = st.number_input("Número de pago", min_value=1, step=1)
        fecha_pago = st.date_input("Fecha del pago", datetime.date.today())
        capital = st.number_input("Capital", min_value=0.01, step=0.01)

        estado_pago = st.selectbox("Estado", ["Pendiente", "Pagado"])

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
                interes_por_10,
                estado_pago
            ))

            con.commit()
            st.success("💰 Pago registrado correctamente")
            time.sleep(0.5)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar pago: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'con' in locals() and con.is_connected():
                con.close()
