import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import time

# ================================
# REGISTRAR MIEMBROS
# ================================
def registrar_miembros():
    # -------------------------------
    # Validar sesión y grupo
    # -------------------------------
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo desconocido")

    # -------------------------------
    # Títulos centrados
    # -------------------------------
    st.markdown(f"<h2 style='text-align:center;'>📌 Grupo: {nombre_grupo}</h2>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>🧍 Registro de Miembros</h1>", unsafe_allow_html=True)

    # -------------------------------
    # Formulario nuevo miembro
    # -------------------------------
    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo")
        dui = st.text_input("DUI")
        telefono = st.text_input("Teléfono")
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
            time.sleep(0.5)
        finally:
            cursor.close()
            con.close()

    # -------------------------------
    # Mostrar tabla y acciones
    # -------------------------------
    mostrar_tabla_y_acciones(id_grupo)


# ================================
# MOSTRAR TABLA Y ACCIONES
# ================================
def mostrar_tabla_y_acciones(id_grupo):
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT M.id_miembro, M.nombre, M.dui, M.telefono
            FROM Miembros M
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY M.nombre
        """, (id_grupo,))
        resultados = cursor.fetchall()
        df = pd.DataFrame(resultados, columns=["ID", "Nombre", "DUI", "Teléfono"])

        if df.empty:
            st.info("Aún no hay miembros en este grupo.")
            return

        # -------------------------------
        # Título
        # -------------------------------
        st.markdown("<h3 style='text-align:center;'>📋 Lista de Miembros Registrados</h3>", unsafe_allow_html=True)

        # -------------------------------
        # Numeración
        # -------------------------------
        df_display = df.copy()
        df_display.insert(0, "No.", range(1, len(df_display) + 1))
        st.dataframe(df_display.drop(columns="ID"), use_container_width=True)

        # -------------------------------
        # Inicializar variables de sesión
        # -------------------------------
        if "editar_id" not in st.session_state:
            st.session_state["editar_id"] = None
        if "eliminar_id" not in st.session_state:
            st.session_state["eliminar_id"] = None

        # -------------------------------
        # Selección de miembro
        # -------------------------------
        miembro_dict = {f"{row['Nombre']} ({row['DUI']})": row for idx, row in df.iterrows()}
        seleccionado = st.selectbox("Selecciona un miembro para Editar/Eliminar", options=list(miembro_dict.keys()))

        if seleccionado:
            miembro = miembro_dict[seleccionado]
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Editar Miembro"):
                    st.session_state["editar_id"] = miembro["ID"]
            with col2:
                if st.button("Eliminar Miembro"):
                    st.session_state["eliminar_id"] = miembro["ID"]

        # -------------------------------
        # Ejecutar edición
        # -------------------------------
        if st.session_state["editar_id"]:
            fila = df[df["ID"] == st.session_state["editar_id"]].iloc[0]
            editar_miembro(fila)
            st.session_state["editar_id"] = None

        # -------------------------------
        # Ejecutar eliminación
        # -------------------------------
        if st.session_state["eliminar_id"]:
            eliminar_miembro(st.session_state["eliminar_id"], id_grupo)
            st.success("Miembro eliminado ✔️")
            st.session_state["eliminar_id"] = None
            time.sleep(0.5)
            # Volver a mostrar la tabla actualizada
            mostrar_tabla_y_acciones(id_grupo)

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
            time.sleep(0.5)
        finally:
            cursor.close()
            con.close()
