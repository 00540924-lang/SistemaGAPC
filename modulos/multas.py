import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import time
from datetime import datetime

# ================================
# MÓDULO MULTAS
# ================================
def multas_modulo():
    # ================================
    # VALIDAR SESIÓN Y GRUPO
    # ================================
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo desconocido")

    st.markdown(f"<h2 style='text-align:center;'>💸 Grupo: {nombre_grupo}</h2>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>📋 Gestión de Multas</h1>", unsafe_allow_html=True)

    # ================================
    # EDITAR MULTA
    # ================================
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

    miembro_seleccionado = st.selectbox("Selecciona un miembro", options=list(miembro_dict.keys()))
    fecha = st.date_input("Fecha de la multa")
    monto = st.number_input("Monto a pagar", min_value=0.0, step=0.01)
    pagada = st.selectbox("¿Pagada?", options=["No", "Sí"])
  
    if st.button("💾 Registrar Multa"):
        try:
            con = obtener_conexion()
            cursor = con.cursor()
            fecha_str = fecha.strftime("%Y-%m-%d")
            pagada_val = 1 if pagada == "Sí" else 0  # ✅ Convertir a entero
            cursor.execute("""
                INSERT INTO Multas (id_miembro, fecha, monto_a_pagar, pagada)
                VALUES (%s, %s, %s, %s)
            """, (miembro_dict[miembro_seleccionado], fecha_str, monto, pagada_val))
            con.commit()
            st.success("Multa registrada correctamente ✔️")
            time.sleep(0.5)
            st.rerun()
        finally:
            cursor.close()
            con.close()
    # ------------------ BOTÓN REGRESAR ------------------
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
    st.write("---")
    # ================================
    # TABLA DE MULTAS
    # ================================
    mostrar_tabla_multas(id_grupo)

# ================================
# FUNCIONES AUXILIARES
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
        # Convertir pagada a Sí/No para mostrar en tabla
        df = pd.DataFrame(resultados, columns=["ID", "Miembro", "Fecha", "Monto", "Pagada"])
        df["Pagada"] = df["Pagada"].apply(lambda x: "Sí" if x == 1 else "No")

        if df.empty:
            st.info("No hay multas registradas en este grupo.")
            return

        df_display = df.reset_index(drop=True)
        df_display.insert(0, "No.", range(1, len(df_display) + 1))

        st.markdown("<h3 style='text-align:center;'>📄 Multas Registradas</h3>", unsafe_allow_html=True)
        st.dataframe(df_display[["No.", "Miembro", "Fecha", "Monto", "Pagada"]].style.hide(axis="index"), use_container_width=True)

        # Selección para editar/eliminar
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


def eliminar_multa(id_multa):
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("DELETE FROM Multas WHERE id_multa = %s", (id_multa,))
        con.commit()
    finally:
        cursor.close()
        con.close()


def editar_multa(multa):
    st.markdown(f"<h3>✏️ Editando multa de: {multa['Miembro']}</h3>", unsafe_allow_html=True)

    fecha = st.date_input("Fecha de la multa", value=pd.to_datetime(multa['Fecha']).date())
    monto = st.number_input("Monto a pagar", min_value=0.0, step=0.01, value=float(multa['Monto']))
    pagada = st.selectbox("¿Pagada?", options=["No", "Sí"], index=0 if multa['Pagada'] == "No" else 1)

    if st.button("💾 Actualizar Multa"):
        try:
            con = obtener_conexion()
            cursor = con.cursor()
            fecha_str = fecha.strftime("%Y-%m-%d")
            pagada_val = 1 if pagada == "Sí" else 0
            cursor.execute("""
                UPDATE Multas SET fecha=%s, monto_a_pagar=%s, pagada=%s
                WHERE id_multa=%s
            """, (fecha_str, monto, pagada_val, multa['ID']))
            con.commit()
            st.success("Multa actualizada correctamente ✔️")
            time.sleep(0.5)
            del st.session_state["editar_multa"]
            st.rerun()
        finally:
            cursor.close()
            con.close()
