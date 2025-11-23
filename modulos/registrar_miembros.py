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
    st.markdown(f"<h2 style='text-align:center; color:#4C3A60;'>📌 Grupo: {nombre_grupo}</h2>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#4C3A60;'>🧍 Registro de Miembros</h1>", unsafe_allow_html=True)

    # ================================
    # FORMULARIO NUEVO MIEMBRO SOLO SI NO ESTAMOS EDITANDO
    # ================================
    if "editar_miembro" not in st.session_state:
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
                st.rerun()  # recarga automática

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
    # Mostrar tabla y acciones
    # ================================
    mostrar_tabla_y_acciones(id_grupo)


def mostrar_tabla_y_acciones(id_grupo):
    # 🔥 Si estamos editando, mostrar solo el formulario de edición y salir
    if "editar_miembro" in st.session_state:
        editar_miembro(st.session_state["editar_miembro"])
        return

    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT M.id_miembro, M.nombre, M.dui, M.telefono
            FROM Miembros M
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY M.id_miembro
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
        # Numeración desde 1
        # -------------------------------
        df_display = df.reset_index(drop=True)
        df_display.insert(0, "No.", range(1, len(df_display) + 1))

        # -------------------------------
        # Mostrar tabla
        # -------------------------------
        st.dataframe(
            df_display[["No.", "Nombre", "DUI", "Teléfono"]].style.hide(axis="index"),
            use_container_width=True
        )

        # -------------------------------
        # 👉 Solo el nombre en el selectbox
        # -------------------------------
        miembro_dict = {row['Nombre']: row for _, row in df.iterrows()}

        seleccionado = st.selectbox(
            "Selecciona un miembro para Editar/Eliminar",
            options=list(miembro_dict.keys())
        )

        if seleccionado:
            miembro = miembro_dict[seleccionado]
            col1, col2 = st.columns(2)

            with col1:
                if st.button(" ✏️ Editar"):
                    st.session_state["editar_miembro"] = miembro
                    st.rerun()  # 🔥 activa modo edición

            with col2:
                if st.button("🗑️ Eliminar"):
                    eliminar_miembro(miembro["ID"], id_grupo)
                    st.success(f"Miembro '{miembro['Nombre']}' eliminado ✔️")
                    time.sleep(0.5)
                    st.rerun()

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

        # 1️⃣ Borrar relaciones con el grupo
        cursor.execute(
            "DELETE FROM Grupomiembros WHERE id_miembro = %s",
            (id_miembro,)
        )

        # 2️⃣ Borrar otras relaciones dependientes si existen
        # 🔹 Ajusta estas tablas según tu base de datos
        cursor.execute(
            "DELETE FROM Asistencias WHERE id_miembro = %s",
            (id_miembro,)
        )
        cursor.execute(
            "DELETE FROM Pagos WHERE id_miembro = %s",
            (id_miembro,)
        )

        # 3️⃣ Finalmente, eliminar el miembro
        cursor.execute(
            "DELETE FROM Miembros WHERE id_miembro = %s",
            (id_miembro,)
        )

        # Confirmar cambios
        con.commit()

    finally:
        cursor.close()
        con.close()


# ================================
# EDITAR MIEMBRO
# ================================
def editar_miembro(row):
    st.markdown(f"<h3>✏️ Editando miembro: {row['Nombre']}</h3>", unsafe_allow_html=True)

    with st.form("form_editar"):
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

            # 🔥 salir del modo edición
            del st.session_state["editar_miembro"]

            st.rerun()

        finally:
            cursor.close()
            con.close()
