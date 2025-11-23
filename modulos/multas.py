import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import time
from datetime import datetime

# ================================
# MÓDULO MULTAS
# ================================
def multas_modulo():

    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo desconocido")

    st.markdown(f"<h2 style='text-align:center;'> 📌 Grupo: {nombre_grupo}</h2>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'> 💸 Gestión de Multas</h1>", unsafe_allow_html=True)

    if "editar_multa" in st.session_state:
        editar_multa(st.session_state["editar_multa"])
        return

    # ================================
    # FORMULARIO NUEVA MULTA
    # ================================
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT M.id_miembro, M.nombre
            FROM Miembros M
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY M.nombre
        """, (id_grupo,))

        miembros = cursor.fetchall()
        miembro_dict = {nombre: id_miembro for id_miembro, nombre in miembros}

    finally:
        cursor.close()
        con.close()

    if not miembros:
        st.info("No hay miembros en este grupo para asignar multas.")
        return

    st.subheader("➕ Registrar nueva multa")

    miembro_seleccionado = st.selectbox("Selecciona un miembro", options=list(miembro_dict.keys()))
    fecha = st.date_input("Fecha de la multa")
    monto = st.number_input("Monto a pagar", min_value=0.0, step=0.01)

    if st.button("💾 Registrar Multa"):
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            fecha_str = fecha.strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO Multas (id_miembro, fecha, monto_a_pagar, pagada)
                VALUES (%s, %s, %s, 0)
            """, (miembro_dict[miembro_seleccionado], fecha_str, monto))

            con.commit()
            st.success("Multa registrada correctamente ✔️")
            time.sleep(0.5)
            st.rerun()

        finally:
            cursor.close()
            con.close()

    st.write("---")

    mostrar_tabla_multas(id_grupo)

    st.write("---")
    st.subheader("💰 Pagar Multa")
    mostrar_multas_pendientes(id_grupo)


# ================================
# MOSTRAR TABLA DE MULTAS (EDITAR/ELIMINAR)
# ================================
def mostrar_tabla_multas(id_grupo):
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT MT.id_multa, M.nombre, MT.fecha, MT.monto_a_pagar, MT.pagada
            FROM Multas MT
            JOIN Miembros M ON MT.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY MT.id_multa
        """, (id_grupo,))

        resultados = cursor.fetchall()

        df = pd.DataFrame(resultados, columns=["ID", "Miembro", "Fecha", "Monto", "Pagada"])

        if df.empty:
            st.info("No hay multas registradas.")
            return

        df_display = df.copy()
        df_display["Estado"] = df_display["Pagada"].apply(lambda x: "Pagada" if x == 1 else "Pendiente")
        df_display.insert(0, "No.", range(1, len(df_display) + 1))

        st.markdown("<h3 style='text-align:center;'>📄 Multas Registradas</h3>", unsafe_allow_html=True)
        st.dataframe(df_display[["No.", "Miembro", "Fecha", "Monto", "Estado"]].style.hide(axis="index"), 
                     use_container_width=True)

        # Selección
        multa_dict = {f"{row['Miembro']} - {row['Fecha']}": row for _, row in df.iterrows()}
        seleccionado = st.selectbox("Selecciona una multa", options=list(multa_dict.keys()))

        if seleccionado:
            multa = multa_dict[seleccionado]

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✏️ Editar", key=f"editar_{multa['ID']}"):
                    st.session_state["editar_multa"] = multa
                    st.rerun()

            with col2:
                if st.button("🗑️ Eliminar", key=f"eliminar_{multa['ID']}"):
                    eliminar_multa(multa["ID"])
                    st.success("Multa eliminada ✔️")
                    time.sleep(0.5)
                    st.rerun()

    finally:
        cursor.close()
        con.close()


# ================================
# NUEVA SECCIÓN — PAGAR MULTA
# ================================
def mostrar_multas_pendientes(id_grupo):
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT MT.id_multa, M.nombre, MT.fecha, MT.monto_a_pagar
            FROM Multas MT
            JOIN Miembros M ON MT.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s AND MT.pagada = 0
            ORDER BY MT.id_multa
        """, (id_grupo,))

        pendientes = cursor.fetchall()

    finally:
        cursor.close()
        con.close()

    if not pendientes:
        st.info("✔ No hay multas pendientes de pago.")
        return

    df = pd.DataFrame(pendientes, columns=["ID", "Miembro", "Fecha", "Monto"])
    df.insert(0, "No.", range(1, len(df) + 1))

    st.dataframe(df.style.hide(axis="index"), use_container_width=True)

    opciones = {f"{row['Miembro']} - {row['Fecha']} - ${row['Monto']}": row for _, row in df.iterrows()}
    seleccion = st.selectbox("Selecciona una multa para pagar:", options=list(opciones.keys()))

    multa = opciones[seleccion]

    if st.button("💵 Pagar multa", key=f"pagar_{multa['ID']}"):
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("UPDATE Multas SET pagada = 1 WHERE id_multa = %s", (multa["ID"],))
            con.commit()

            st.success("Multa pagada correctamente ✔️")
            time.sleep(0.5)
            st.rerun()

        finally:
            cursor.close()
            con.close()


# ================================
# ELIMINAR MULTA
# ================================
def eliminar_multa(id_multa):
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("DELETE FROM Multas WHERE id_multa = %s", (id_multa,))
        con.commit()

    finally:
        cursor.close()
        con.close()


# ================================
# EDITAR MULTA
# ================================
def editar_multa(multa):
    st.markdown(f"<h3>✏️ Editando multa de: {multa['Miembro']}</h3>", unsafe_allow_html=True)

    fecha = st.date_input("Fecha de la multa", value=pd.to_datetime(multa['Fecha']).date())
    monto = st.number_input("Monto a pagar", min_value=0.0, step=0.01, value=float(multa['Monto']))

    if st.button("💾 Actualizar Multa"):
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            fecha_str = fecha.strftime("%Y-%m-%d")

            cursor.execute("""
                UPDATE Multas
                SET fecha=%s, monto_a_pagar=%s
                WHERE id_multa=%s
            """, (fecha_str, monto, multa['ID']))

            con.commit()

            st.success("Multa actualizada correctamente ✔️")
            time.sleep(0.5)
            del st.session_state["editar_multa"]
            st.rerun()

        finally:
            cursor.close()
            con.close()
 # ------------------ BOTÓN REGRESAR ------------------
    if st.button("⬅️ Regresar al Menú"):
        # Limpiamos el estado de edición
        if "editar_multa" in st.session_state:
            del st.session_state["editar_multa"]
        # Redirigimos al menú
        st.session_state["page"] = "menu"
        st.rerun()
