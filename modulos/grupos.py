import mysql.connector
import streamlit as st

# ==========================
#  CONEXIÓN A BASE DE DATOS
# ==========================
def get_connection():
    return mysql.connector.connect(
        host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
        user="uiazxdhtd3r8o7uv",
        password="uGjZ9MXWemv7vPsjOdA5",
        database="bzn5gsi7ken7lufcglbg"
    )

# ==========================
#  PÁGINA PRINCIPAL
# ==========================
def pagina_grupos():
    st.title("Gestión de Grupos")

    # -----------------------------------------------------
    # BOTÓN PARA REGRESAR AL MENÚ PRINCIPAL
    # -----------------------------------------------------
    if st.button("⬅️ Regresar al menú", key="btn_regresar_menu"):
        st.session_state["page"] = "menu"
        st.rerun()

    st.write("---")

    # ---------------------------------------------
    # FORMULARIO PARA CREAR GRUPO
    # ---------------------------------------------
    st.subheader("➕ Registrar nuevo grupo")

    nombre = st.text_input("Nombre del Grupo", key="input_nombre_grupo")
    distrito = st.text_input("Distrito", key="input_distrito")
    inicio_ciclo = st.date_input("Inicio del Ciclo", key="input_inicio_ciclo")

    if st.button("Guardar grupo", key="btn_guardar_grupo"):
        if not nombre.strip():
            st.error("El nombre del grupo es obligatorio.")
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Grupos (nombre_grupo, distrito, inicio_ciclo) VALUES (%s, %s, %s)",
                (nombre, distrito, inicio_ciclo)
            )
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Grupo registrado correctamente")
            st.experimental_rerun()

    st.write("---")

    # ---------------------------------------------
    # SECCIÓN: GESTIONAR MIEMBROS DE UN GRUPO
    # ---------------------------------------------
    st.subheader("👥 Gestionar miembros de grupos")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id_grupo, nombre_grupo FROM Grupos")
    grupos = cursor.fetchall()

    if not grupos:
        cursor.close()
        conn.close()
        st.info("No hay grupos registrados aún.")
        return

    grupo_seleccionado = st.selectbox(
        "Selecciona un grupo",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x),
        key="select_grupo"
    )

    # --------------------------------------------------------
    # BOTÓN PARA INICIAR EL PROCESO DE ELIMINAR EL GRUPO COMPLETO
    # --------------------------------------------------------
    st.write("### Opciones del grupo seleccionado")

    # Botón inicial de eliminación (pone flag en session_state)
    if st.button("🗑️ Eliminar grupo", key=f"btn_iniciar_eliminar_{grupo_seleccionado}"):
        st.session_state["confirmar_eliminar"] = True
        st.session_state["grupo_a_eliminar"] = grupo_seleccionado

    # Si el flag está puesto, mostramos confirmación con botones
    if st.session_state.get("confirmar_eliminar", False):
        st.warning("⚠️ ¿Estás seguro de que deseas eliminar este grupo? Esta acción no se puede deshacer.")

        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Sí, eliminar (confirmar)", key=f"btn_confirmar_eliminar_{st.session_state.get('grupo_a_eliminar')}"):
                grupo_id_eliminar = st.session_state.get("grupo_a_eliminar")
                try:
                    # eliminar miembros relacionados primero
                    cursor.execute("DELETE FROM Grupomiembros WHERE id_grupo = %s", (grupo_id_eliminar,))
                    # luego eliminar grupo
                    cursor.execute("DELETE FROM Grupos WHERE id_grupo = %s", (grupo_id_eliminar,))
                    conn.commit()
                    st.success("Grupo eliminado correctamente.")
                except Exception as e:
                    st.error(f"Error al eliminar el grupo: {e}")
                finally:
                    st.session_state["confirmar_eliminar"] = False
                    st.session_state.pop("grupo_a_eliminar", None)
                    cursor.close()
                    conn.close()
                    st.experimental_rerun()

        with col_no:
            if st.button("Cancelar", key=f"btn_cancelar_eliminar_{st.session_state.get('grupo_a_eliminar')}"):
                st.session_state["confirmar_eliminar"] = False
                st.session_state.pop("grupo_a_eliminar", None)
                st.info("Eliminación cancelada.")

    st.write("### Miembros del grupo")

    # ---------------------------------------------
    # OBTENER MIEMBROS DEL GRUPO
    # ---------------------------------------------
    cursor.execute("""
        SELECT M.id_miembro, M.nombre
        FROM Grupomiembros GM
        JOIN Miembros M ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
    """, (grupo_seleccionado,))
    miembros_grupo = cursor.fetchall()

    # ------------------------------------------------------------
    # LISTADO DE MIEMBROS + BOTÓN PARA ELIMINAR
    # ------------------------------------------------------------
    if miembros_grupo:
        for m in miembros_grupo:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"✔️ {m['nombre']}")
            with col2:
                if st.button("❌", key=f"del_{grupo_seleccionado}_{m['id_miembro']}"):
                    try:
                        cursor.execute(
                            "DELETE FROM Grupomiembros WHERE id_grupo = %s AND id_miembro = %s",
                            (grupo_seleccionado, m["id_miembro"])
                        )
                        conn.commit()
                        st.success(f"{m['nombre']} eliminado del grupo.")
                        cursor.close()
                        conn.close()
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar miembro: {e}")
    else:
        st.info("Este grupo aún no tiene miembros.")

    st.write("---")

    # ---------------------------------------------
    # AGREGAR MIEMBROS AL GRUPO
    # ---------------------------------------------
    st.write("### ➕ Agregar miembros al grupo")

    cursor.execute("SELECT id_miembro, nombre FROM Miembros")
    todos_miembros = cursor.fetchall()

    ids_actuales = [m["id_miembro"] for m in miembros_grupo]

    # Filtrar miembros NO presentes en el grupo
    miembros_disponibles = [m for m in todos_miembros if m["id_miembro"] not in ids_actuales]

    if miembros_disponibles:
        nuevos = st.multiselect(
            "Selecciona miembros para agregar",
            options=[m["id_miembro"] for m in miembros_disponibles],
            format_func=lambda x: next(m["nombre"] for m in miembros_disponibles if m["id_miembro"] == x),
            key=f"multiselect_agregar_{grupo_seleccionado}"
        )

        if st.button("Agregar al grupo", key=f"btn_agregar_{grupo_seleccionado}"):
            try:
                for id_miembro in nuevos:
                    cursor.execute(
                        "INSERT INTO Grupomiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                        (grupo_seleccionado, id_miembro)
                    )
                conn.commit()
                st.success("Miembros agregados correctamente.")
                cursor.close()
                conn.close()
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error al agregar miembros: {e}")
    else:
        st.info("Todos los miembros ya están en este grupo.")

    cursor.close()
    conn.close()
