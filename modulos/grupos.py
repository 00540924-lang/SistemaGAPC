import streamlit as st
import time
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
    nombre = st.text_input("Nombre del Grupo", key="nombre_grupo")
    distrito = st.text_input("Distrito", key="distrito")
    inicio_ciclo = st.date_input("Inicio del Ciclo", key="inicio_ciclo")

    if st.button("Guardar grupo"):
        mensaje = st.empty()
        if not nombre.strip():
            mensaje.error("El nombre del grupo es obligatorio.")
            time.sleep(3)
            mensaje.empty()
        else:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Grupos (nombre_grupo, distrito, inicio_ciclo) VALUES (%s, %s, %s)",
                    (nombre, distrito, inicio_ciclo)
                )
                conn.commit()
                mensaje.success("Grupo creado correctamente.")
                time.sleep(3)
                mensaje.empty()
            except Exception as e:
                mensaje.error(f"Error al crear grupo: {e}")
                time.sleep(3)
                mensaje.empty()
            finally:
                cursor.close()
                conn.close()

    st.write("---")

    # ================= LISTAR GRUPOS =================
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_grupo, nombre_grupo FROM Grupos")
        grupos = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not grupos:
        st.info("No hay grupos registrados aún.")
        return

    # ================= FORMULARIO NUEVO MIEMBRO =================
    st.subheader("➕ Registrar nuevo miembro")
    with st.form("form_miembro"):
        nombre_m = st.text_input("Nombre completo", key="nombre_miembro")
        dui = st.text_input("DUI", key="dui")
        telefono = st.text_input("Teléfono", key="telefono")
        grupo_asignado = st.selectbox(
            "Asignar al grupo",
            options=[g["id_grupo"] for g in grupos],
            format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x)
        )

        # ✅ Checkbox para marcar si es administrador
        es_admin = st.checkbox("Este miembro también será administrador")

        # Solo aparece si se marca el checkbox
        if es_admin:
            usuario_admin = st.text_input("Usuario para login (admin)")
            contraseña_admin = st.text_input("Contraseña para login (admin)", type="password")

        enviar = st.form_submit_button("Registrar miembro")
        if enviar:
            mensaje = st.empty()
            if not nombre_m.strip():
                mensaje.error("El nombre del miembro es obligatorio.")
                time.sleep(3)
                mensaje.empty()
            else:
                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor(dictionary=True)

                    # ---------------- Insertar miembro ----------------
                    cursor.execute(
                        "INSERT INTO Miembros (nombre, dui, telefono) VALUES (%s, %s, %s)",
                        (nombre_m, dui, telefono)
                    )
                    conn.commit()
                    miembro_id = cursor.lastrowid

                    # ---------------- Crear relación con grupo ----------------
                    cursor.execute(
                        "INSERT INTO Grupomiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                        (grupo_asignado, miembro_id)
                    )
                    conn.commit()

                    # ---------------- Si es administrador ----------------
                    if es_admin:
                        if not usuario_admin or not contraseña_admin:
                            mensaje.warning("Debe ingresar usuario y contraseña para administrador.")
                        else:
                            cursor.execute(
                                "INSERT INTO Administradores (Usuario, Contraseña, Rol) VALUES (%s, %s, %s)",
                                (usuario_admin, contraseña_admin, "institucional")
                            )
                            conn.commit()
                            id_adm = cursor.lastrowid

                            # Actualizar Miembros con id_administrador
                            cursor.execute(
                                "UPDATE Miembros SET id_administrador=%s WHERE id_miembro=%s",
                                (id_adm, miembro_id)
                            )
                            conn.commit()

                    mensaje.success(f"{nombre_m} registrado correctamente en el grupo.")
                    time.sleep(3)
                    mensaje.empty()
                except Exception as e:
                    conn.rollback()
                    mensaje.error(f"Error al registrar miembro: {e}")
                    time.sleep(3)
                    mensaje.empty()
                finally:
                    cursor.close()
                    conn.close()

    st.write("---")

    # ================= LISTAR MIEMBROS DEL GRUPO =================
    st.subheader("🧑‍🤝‍🧑 Miembros por Grupo")
    grupo_seleccionado = st.selectbox(
        "Selecciona un grupo para ver sus miembros",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x),
        key="grupo_lista"
    )

    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT M.id_miembro, M.nombre
            FROM Grupomiembros GM
            JOIN Miembros M ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
        """, (grupo_seleccionado,))
        miembros = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if miembros:
        for m in miembros:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"✔️ {m['nombre']}")
            with col2:
                if st.button("❌", key=f"del_{grupo_seleccionado}_{m['id_miembro']}"):
                    mensaje = st.empty()
                    try:
                        conn = obtener_conexion()
                        cursor = conn.cursor()
                        cursor.execute(
                            "DELETE FROM Grupomiembros WHERE id_grupo=%s AND id_miembro=%s",
                            (grupo_seleccionado, m['id_miembro'])
                        )
                        conn.commit()
                        mensaje.success(f"{m['nombre']} eliminado del grupo.")
                        time.sleep(3)
                        mensaje.empty()
                    finally:
                        cursor.close()
                        conn.close()
    else:
        st.info("Este grupo no tiene miembros.")

    st.write("---")

    # ================= ELIMINAR UN GRUPO =================
    st.subheader("🗑️ Eliminar un grupo completo")
    st.warning("⚠️ Al eliminar un grupo, también se eliminarán los miembros que solo pertenecen a este grupo. Hazlo con cuidado.")

    grupo_eliminar = st.selectbox(
        "Selecciona el grupo a eliminar",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x),
        key="grupo_eliminar"
    )

    if st.button("Eliminar grupo seleccionado"):
        mensaje = st.empty()
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Grupomiembros WHERE id_grupo=%s", (grupo_eliminar,))
            cursor.execute("""
                DELETE FROM Miembros
                WHERE id_miembro NOT IN (SELECT id_miembro FROM Grupomiembros)
            """)
            cursor.execute("DELETE FROM Grupos WHERE id_grupo=%s", (grupo_eliminar,))
            conn.commit()
            mensaje.success("Grupo y miembros asociados eliminados correctamente.")
            time.sleep(3)
            mensaje.empty()
        finally:
            cursor.close()
            conn.close()
