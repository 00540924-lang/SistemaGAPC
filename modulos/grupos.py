import streamlit as st
from modulos.config.conexion import obtener_conexion

def pagina_grupos():
    st.title("Gestión de Grupos")

 # ------------------ BOTÓN REGRESAR ------------------
    st.write("")  # espaciado
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    st.write("---")

    # ================= FORMULARIO NUEVO GRUPO =================
    st.subheader("➕ Registrar nuevo grupo")
    nombre = st.text_input("Nombre del Grupo")
    distrito = st.text_input("Distrito")
    inicio_ciclo = st.date_input("Inicio del Ciclo")

    if st.button("Guardar grupo"):
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

        # ------------------ ELIMINAR GRUPO ------------------
        if st.button("🗑️ Eliminar grupo"):
            st.session_state["confirmar_eliminar"] = True
            st.session_state["grupo_a_eliminar"] = grupo_id

        if st.session_state.get("confirmar_eliminar", False):
            st.warning("⚠️ ¿Seguro que deseas eliminar este grupo? Esto borrará sus miembros.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Sí, eliminar"):
                    gid = st.session_state["grupo_a_eliminar"]
                    try:
                        cursor.execute("DELETE FROM Grupomiembros WHERE id_grupo = %s", (gid,))
                        cursor.execute("DELETE FROM Grupos WHERE id_grupo = %s", (gid,))
                        conn.commit()
                        st.success("Grupo eliminado correctamente.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        st.session_state["confirmar_eliminar"] = False
                        st.session_state.pop("grupo_a_eliminar", None)
                        st.stop()
            with col2:
                if st.button("Cancelar eliminación"):
                    st.session_state["confirmar_eliminar"] = False
                    st.session_state.pop("grupo_a_eliminar", None)
                    st.info("Operación cancelada.")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    st.write("---")

    # ================= FORMULARIO MIEMBROS =================
    st.subheader("➕ Registrar nuevo miembro")
    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo")
        dui = st.text_input("DUI")
        telefono = st.text_input("Teléfono")
        enviar = st.form_submit_button("Registrar")

        if enviar:
            conn = None
            cursor = None
            try:
                conn = obtener_conexion()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "INSERT INTO Miembros (nombre, dui, telefono) VALUES (%s, %s, %s)",
                    (nombre, dui, telefono)
                )
                conn.commit()
                st.success(f"{nombre} registrado correctamente.")
                st.stop()
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    # ================= LISTAR MIEMBROS DEL GRUPO =================
    if 'grupo_id' in locals():
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

            st.write("### 🧑‍🤝‍🧑 Miembros del grupo")
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
                            st.success(f"{m['nombre']} eliminado.")
                            st.stop()
            else:
                st.info("Este grupo no tiene miembros.")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    st.write("---")
