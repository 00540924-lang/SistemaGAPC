import streamlit as st
from modulos.config.conexion import obtener_conexion

def pagina_grupos():
    st.title("Gestión de Grupos")

    # ------------------ BOTÓN REGRESAR ------------------
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        return  # Simplemente regresamos al menú sin recargar

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
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Grupos (nombre_grupo, distrito, inicio_ciclo) VALUES (%s, %s, %s)",
                    (nombre, distrito, inicio_ciclo)
                )
                conn.commit()
                st.success("Grupo creado correctamente.")
                st.session_state["actualizar"] = not st.session_state.get("actualizar", False)
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
                st.session_state["actualizar"] = not st.session_state.get("actualizar", False)
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                cursor.close()
                conn.close()

    st.write("---")

    # ================= LISTAR MIEMBROS DEL GRUPO SELECCIONADO =================
    st.subheader("🧑‍🤝‍🧑 Miembros por Grupo")
    grupo_seleccionado = st.selectbox(
        "Selecciona un grupo para ver sus miembros",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x),
        key="grupo_lista"
    )

    # Obtener miembros del grupo seleccionado
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
                        st.success(f"{m['nombre']} eliminado del grupo.")
                        st.session_state["actualizar"] = not st.session_state.get("actualizar", False)
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        cursor.close()
                        conn.close()
    else:
        st.info("Este grupo no tiene miembros.")

    st.write("---")
