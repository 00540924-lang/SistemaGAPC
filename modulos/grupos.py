import streamlit as st
import mysql.connector

# -----------------------------------------
# CONEXIÓN A BASE DE DATOS
# -----------------------------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sistemagapc"
    )

# -----------------------------------------
# ELIMINAR GRUPO
# -----------------------------------------
def eliminar_grupo(id_grupo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Grupomiembros WHERE id_grupo = %s", (id_grupo,))
    cursor.execute("DELETE FROM grupos WHERE id_grupo = %s", (id_grupo,))
    conn.commit()
    cursor.close()
    conn.close()


# -----------------------------------------
# PÁGINA PRINCIPAL DE GRUPOS
# -----------------------------------------
def pagina_grupos():

    st.title("Gestión de Grupos")

    # Botón regresar al menú
    if st.button("⬅ Regresar al Menú"):
        st.session_state["modulo"] = "menu_principal"
        st.experimental_rerun()

    st.header("Registrar Nuevo Grupo")
    nombre = st.text_input("Nombre del Grupo")
    distrito = st.text_input("Distrito")
    inicio_ciclo = st.date_input("Inicio de Ciclo")

    if st.button("Guardar Grupo"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO grupos (nombre, distrito, inicio_ciclo)
            VALUES (%s, %s, %s)
        """, (nombre, distrito, inicio_ciclo))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Grupo registrado exitosamente.")
        st.experimental_rerun()

    st.header("Grupos Registrados")

    # Cargar grupos
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_grupo, nombre FROM grupos")
    grupos = cursor.fetchall()

    cursor.close()
    conn.close()

    if not grupos:
        st.info("No hay grupos registrados aún.")
        return

    # Selector de grupo
    grupo_seleccionado = st.selectbox(
        "Selecciona un grupo",
        {g[1]: g[0] for g in grupos}
    )

    id_grupo = {g[1]: g[0] for g in grupos}[grupo_seleccionado]

    # Mostrar miembros del grupo
    st.subheader(f"Miembros del Grupo: {grupo_seleccionado}")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT M.id_miembro, M.nombre
        FROM miembros M
        INNER JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
    """, (id_grupo,))
    miembros = cursor.fetchall()
    cursor.close()
    conn.close()

    if miembros:
        for m in miembros:
            st.write(f"- {m[1]}")
    else:
        st.info("Este grupo no tiene miembros aún.")

    # Agregar miembros al grupo
    st.subheader("Agregar Miembro al Grupo")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_miembro, nombre FROM miembros")
    lista_miembros = cursor.fetchall()
    cursor.close()
    conn.close()

    if lista_miembros:
        miembro_seleccionado = st.selectbox(
            "Selecciona un miembro",
            {m[1]: m[0] for m in lista_miembros}
        )

        miembro_id = {m[1]: m[0] for m in lista_miembros}[miembro_seleccionado]

        if st.button("Agregar Miembro"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Grupomiembros (id_grupo, id_miembro)
                VALUES (%s, %s)
            """, (id_grupo, miembro_id))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Miembro agregado correctamente.")
            st.experimental_rerun()
    else:
        st.warning("No hay miembros registrados en el sistema.")

    st.divider()

    # -----------------------------------------
    # ELIMINAR GRUPO
    # -----------------------------------------
    st.subheader("Eliminar Grupo")

    if st.button("🗑 Eliminar Grupo"):
        st.session_state["confirmar_eliminar"] = True
        st.session_state["grupo_a_eliminar"] = id_grupo

    if st.session_state.get("confirmar_eliminar", False):

        st.error("⚠ ¿Seguro que deseas eliminar este grupo? Esta acción NO se puede deshacer.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Sí, eliminar"):
                eliminar_grupo(st.session_state["grupo_a_eliminar"])
                st.session_state["confirmar_eliminar"] = False
                st.success("Grupo eliminado.")
                st.experimental_rerun()

        with col2:
            if st.button("Cancelar"):
                st.session_state["confirmar_eliminar"] = False
                st.info("Eliminación cancelada.")


# FIN DEL ARCHIVO
