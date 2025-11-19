import streamlit as st
from modulos.config.conexion import obtener_conexion

def pagina_grupos():
    st.title("Gestión de Grupos")

    # ------------------ BOTÓN VOLVER AL MENÚ ------------------
    if st.button("⬅️ Regresar al menú"):
        st.session_state["page"] = "menu"
        st.stop()

    st.write("---")

    # ================= FORMULARIO NUEVO GRUPO =================
    st.subheader("➕ Registrar nuevo grupo")
    nombre = st.text_input("Nombre del Grupo", key="nombre_grupo")
    distrito = st.text_input("Distrito", key="distrito")
    inicio_ciclo = st.date_input("Inicio del Ciclo", key="inicio_ciclo")

    if st.button("Guardar grupo", key="guardar_grupo"):
        if not nombre.strip():
            st.error("El nombre del grupo es obligatorio.")
        else:
            conn = None
            cursor = None
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Grupos (nombre_grupo, distrito, inicio_ciclo) VALUES (%s, %s, %s)",
                    (nombre, distrito, inicio_ciclo)
                )
                conn.commit()
                st.success("Grupo creado correctamente.")
                st.stop()
            except Exception as e:
                st.error(f"Error al crear grupo: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    st.write("---")

    # ================= LISTAR GRUPOS =================
    conn = None
    cursor = None
    grupos = []
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_grupo, nombre_grupo FROM Grupos")
        grupos = cursor.fetchall()

        if not grupos:
            st.info("No hay grupos registrados aún.")
            return

        st.write("### ⚙️ Opciones del grupo")
        grupo_id = st.selectbox(
            "Selecciona un grupo",
            options=[g["id_grupo"] for g in grupos],
            format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x)
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    st.write("---")

    # ================= FORMULARIO MIEMBROS =================
    st.subheader("➕ Registrar nuevo miembro")
    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo", key="nombre_miembro")
        dui = st.text_input("DUI", key="dui")
        telefono = st.text_input("Teléfono", key="telefono")
        grupo_asignado = st.selectbox(
            "Asignar al grupo",
            options=[g["id_grupo"] for g in grupos],
            format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x),
            key="grupo_asignado"
        )
        enviar = st.form_submit_button("Registrar")

        if enviar:
            conn = None
            cursor = None
            try:
                conn = obtener_conexion()
                cursor = conn.cursor(dictionary=True)
                # Insertar miembro
                cursor.execute(
                    "INSERT INTO Miembros (nombre, dui, telefono) VALUES (%s, %s, %s)",
                    (nombre, dui, telefono)
                )
                conn.commit()
                miembro_id = cursor.lastrowid

                # Asignar al grupo seleccionado
                cursor.execute(
                    "INSERT INTO Grupomiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                    (grupo_asignado, miembro_id)
                )
                conn.commit()
                st.success(f"{nombre} registrado correctamente en el grupo.")

                st.stop()
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    st.write("---")

    # ================= LISTAR MIEMBROS DEL GRUPO SELECCIONADO =================
    if grupo_id:
        conn = None
        cursor = None
        try:
            conn = obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT M.id_miembro, M.nombre
                FROM Grupomiembros GM
                JOIN Miembros M ON GM.id_miembro = M.id_miembro
                WHERE GM.id_grupo = %s
            """, (grupo_id,))
            miembros = cursor.fetchall()

            st.write("### 🧑‍🤝‍🧑 Miembros del grupo seleccionado")
            if miembros:
                for m in miembros:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"✔️ {m['nombre']}")
                    with col2:
                        if st.button("❌", key=f"del_{grupo_id}_{m['id_miembro']}"):
                            cursor.execute(
                                "DELETE FROM Grupomiembros WHERE id_grupo = %s AND id_miembro = %s",
                                (grupo_id, m["id_miembro"])
                            )
                            conn.commit()
                            st.success(f"{m['nombre']} eliminado del grupo.")
                            st.stop()
            else:
                st.info("Este grupo no tiene miembros.")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    st.write("---")
