import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import time

def registrar_miembros():
    # ================================
    # VALIDAR SESIÓN Y GRUPO
    # ================================
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo desconocido")

    # ================================
    # TITULOS CENTRADOS
    # ================================
    st.markdown(f"<h2 style='text-align:center;'>📌 Grupo: {nombre_grupo}</h2>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>🧍 Registro de Miembros</h1>", unsafe_allow_html=True)

    # ================================
    # FORMULARIO NUEVO MIEMBRO
    # ================================
    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo")
        dui = st.text_input("DUI")
        telefono = st.text_input("Telefono")
        enviar = st.form_submit_button("Registrar")

    if enviar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO Miembros (Nombre, DUI, Telefono) VALUES (%s, %s, %s)",
                (nombre, dui, telefono)
            )
            con.commit()
            id_miembro = cursor.lastrowid
            cursor.execute(
                "INSERT INTO Grupomiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                (id_grupo, id_miembro)
            )
            con.commit()
            st.success("Miembro registrado correctamente ✔️")
            time.sleep(1)
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            cursor.close()
            con.close()

    # ================================
    # MOSTRAR MIEMBROS COMO TABLA
    # ================================
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT M.id_miembro, M.nombre, M.dui, M.telefono
            FROM Miembros M
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
        """, (id_grupo,))
        resultados = cursor.fetchall()
        df = pd.DataFrame(resultados, columns=["ID", "Nombre", "DUI", "Teléfono"])

        if df.empty:
            st.info("Aún no hay miembros en este grupo.")
        else:
            # -------------------------------
            # Cabecera de la tabla
            # -------------------------------
            col_headers = st.columns([1, 3, 2, 2, 2])
            headers = ["No.", "Nombre", "DUI", "Teléfono", "Acciones"]
            for col, header in zip(col_headers, headers):
                col.markdown(f"**{header}**")

            # -------------------------------
            # Filas de la tabla
            # -------------------------------
            for idx, row in df.iterrows():
                cols = st.columns([1, 3, 2, 2, 2])
                cols[0].markdown(f"{idx+1}")
                cols[1].markdown(row["Nombre"])
                cols[2].markdown(row["DUI"])
                cols[3].markdown(row["Teléfono"])
                with cols[4]:
                    if st.button("Editar", key=f"editar_{row['ID']}"):
                        editar_miembro(row)
                        st.experimental_rerun()
                    if st.button("Eliminar", key=f"eliminar_{row['ID']}"):
                        eliminar_miembro(row["ID"], id_grupo)
                        st.experimental_rerun()

    finally:
        cursor.close()
        con.close()


# ================================
# ELIMINAR MIEMBRO
# ================================
def eliminar_miembro(id_miembro, id_grupo):
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute(
            "DELETE FROM Grupomiembros WHERE id_grupo = %s AND id_miembro = %s",
            (id_grupo, id_miembro)
        )
        con.commit()
        cursor.execute(
            "DELETE FROM Miembros WHERE id_miembro = %s",
            (id_miembro,)
        )
        con.commit()
        st.success("Miembro eliminado ✔️")
    finally:
        cursor.close()
        con.close()


# ================================
# EDITAR MIEMBRO
# ================================
def editar_miembro(row):
    st.markdown(f"<h3>✏️ Editando miembro: {row['Nombre']}</h3>", unsafe_allow_html=True)
    with st.form(f"form_editar_{row['ID']}"):
        nombre = st.text_input("Nombre completo", value=row['Nombre'])
        dui = st.text_input("DUI", value=row['DUI'])
        telefono = st.text_input("Teléfono", value=row['Teléfono'])
        actualizar = st.form_submit_button("Actualizar")

    if actualizar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()
            cursor.execute(
                "UPDATE Miembros SET Nombre=%s, DUI=%s, Telefono=%s WHERE id_miembro=%s",
                (nombre, dui, telefono, row['ID'])
            )
            con.commit()
            st.success("Miembro actualizado correctamente ✔️")
            time.sleep(1)
            st.experimental_rerun()
        finally:
            cursor.close()
            con.close()
