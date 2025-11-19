import streamlit as st
from modulos.config.conexion import obtener_conexion

def pagina_grupos():
    st.title("Gestión de Grupos")

    # ------------------ BOTÓN REGRESAR ------------------
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        return
    st.write("---")

    # ================= FORMULARIO NUEVO GRUPO =================
    st.subheader("➕ Registrar nuevo grupo")
    nombre = st.text_input("Nombre del Grupo", key="nombre_grupo")
    distrito = st.text_input("Distrito", key="distrito")
    inicio_ciclo = st.date_input("Inicio del Ciclo", key="inicio_ciclo")

    if st.button("Guardar grupo"):
        if not nombre.strip():
            st.error("El nombre del grupo es obligatorio.")
        else:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Grupos (nombre_grupo, distrito, inicio_ciclo) VALUES (%s, %s, %s)",
                    (nombre, distrito, inicio_ciclo)
                )
                conn.commit()
                st.success("Grupo creado correctamente.")
            except Exception as e:
                st.error(f"Error al crear grupo: {e}")
            finally:
                cursor.close()
                conn.close()

    st.write("---")

    # ================= LISTAR GRUPOS =================
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_grupo, nombre_grupo FROM Grupos")
    grupos = cursor.fetchall()
    cursor.close()
    conn.close()

    if not grupos:
        st.info("No hay grupos registrados aún.")
        return

    # ================= LISTAR MIEMBROS DEL GRUPO =================
    st.subheader("🧑‍🤝‍🧑 Miembros por Grupo")
    grupo_seleccionado = st.selectbox(
        "Selecciona un grupo para ver sus miembros",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x),
        key="grupo_lista"
    )

    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT M.id_miembro, M.nombre
        FROM Grupomiembros GM
        JOIN Miembros M ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
    """, (grupo_seleccionado,))
    miembros = cursor.fetchall()
    cursor.close()
    conn.close()

    if miembros:
        for m in miembros:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"✔️ {m['nombre']}")
            with col2:
                if st.button("❌", key=f"del_{grupo_seleccionado}_{m['id_miembro']}"):
                    try:
                        conn = obtener_conexion()
                        cursor = conn.cursor()
                        cursor.execute(
                            "DELETE FROM Grupomiembros WHERE id_grupo = %s AND id_miembro = %s",
                            (grupo_seleccionado, m["id_miembro"])
                        )
                        conn.commit()
                        st.experimental_rerun()  # Esto recarga la app con la lista actualizada
                    finally:
                        cursor.close()
                        conn.close()
    else:
        st.info("Este grupo no tiene miembros.")

    st.write("---")

    # ================= ELIMINAR UN GRUPO =================
    st.subheader("🗑️ Eliminar un grupo completo")
    grupo_eliminar = st.selectbox(
        "Selecciona un grupo para eliminar",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x),
        key="grupo_eliminar"
    )

    if "confirmar_eliminar" not in st.session_state:
        st.session_state["confirmar_eliminar"] = False

    if st.button("Eliminar grupo seleccionado"):
        st.session_state["confirmar_eliminar"] = True

    if st.session_state["confirmar_eliminar"]:
        st.warning(
            "⚠️ ¿Seguro que deseas eliminar este grupo? Esto eliminará también a los miembros que solo pertenecen a este grupo."
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sí, eliminar"):
                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    grupo_id = grupo_eliminar

                    # Eliminar relaciones
                    cursor.execute("DELETE FROM Grupomiembros WHERE id_grupo = %s", (grupo_id,))
                    cursor.execute("DELETE FROM Grupos WHERE id_grupo = %s", (grupo_id,))
                    conn.commit()
                    st.success("Grupo eliminado correctamente.")
                finally:
                    cursor.close()
                    conn.close()
                    st.session_state["confirmar_eliminar"] = False
                    st.experimental_rerun()  # Recarga la app con la lista actualizada

        with col2:
            if st.button("Cancelar"):
                st.session_state["confirmar_eliminar"] = False
                st.info("Operación cancelada.")
