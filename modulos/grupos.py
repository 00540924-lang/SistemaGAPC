import streamlit as st
import sqlite3

# -------------------------------------
# CONEXIÓN A BASE DE DATOS
# -------------------------------------
def obtener_conexion():
    return sqlite3.connect("database.db", check_same_thread=False)

# -------------------------------------
# FUNCIÓN PARA MOSTRAR LOS GRUPOS
# -------------------------------------
def obtener_grupos():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM Grupomiembros")
    grupos = cursor.fetchall()
    conn.close()
    return grupos

# -------------------------------------
# FUNCIÓN PARA CREAR GRUPO
# -------------------------------------
def crear_grupo(nombre):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Grupomiembros (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()

# -------------------------------------
# FUNCIÓN PARA ELIMINAR GRUPO
# -------------------------------------
def eliminar_grupo(id_grupo):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Grupomiembros WHERE id = ?", (id_grupo,))
    conn.commit()
    conn.close()

# -------------------------------------
# PÁGINA PRINCIPAL DE GRUPOS
# -------------------------------------
def pagina_grupos():

    st.title("Gestión de Grupos")

    # -------------------------------------
    # BOTÓN REGRESAR AL MENÚ
    # -------------------------------------
    if st.button("⬅️ Regresar al menú"):
        st.session_state["modulo"] = None
        st.experimental_rerun()

    st.subheader("Crear nuevo grupo")

    nuevo_grupo = st.text_input("Nombre del grupo")

    if st.button("Crear grupo"):
        if nuevo_grupo.strip() != "":
            crear_grupo(nuevo_grupo)
            st.success("Grupo creado exitosamente.")
            st.experimental_rerun()
        else:
            st.error("El nombre del grupo no puede estar vacío.")

    st.subheader("Listado de Grupos")

    grupos = obtener_grupos()

    if not grupos:
        st.info("No hay grupos registrados aún.")
        return

    for grupo in grupos:
        id_grupo, nombre = grupo

        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(f"**{nombre}**")

        with col2:
            if st.button("🗑️ Eliminar", key=f"del_{id_grupo}"):
                st.session_state["grupo_a_eliminar"] = id_grupo
                st.session_state["confirmar_eliminar"] = True

    # -------------------------------------
    # DIÁLOGO DE CONFIRMACIÓN
    # -------------------------------------
    if st.session_state.get("confirmar_eliminar", False):

        st.warning("⚠️ ¿Estás seguro de que deseas eliminar este grupo? Esta acción es irreversible.")

        colA, colB = st.columns(2)

        with colA:
            if st.button("Sí, eliminar"):
                eliminar_grupo(st.session_state["grupo_a_eliminar"])
                st.success("Grupo eliminado exitosamente.")
                st.session_state["confirmar_eliminar"] = False
                st.experimental_rerun()

        with colB:
            if st.button("Cancelar"):
                st.session_state["confirmar_eliminar"] = False
                st.info("Eliminación cancelada.")

