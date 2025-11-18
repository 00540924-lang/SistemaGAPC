import mysql.connector
import streamlit as st
from datetime import date

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

    # BOTÓN PARA VOLVER AL MENÚ
    if st.button("⬅️ Regresar al menú"):
        st.session_state["page"] = "menu"
        st.experimental_rerun()

    st.write("---")

    # =========================================
    # FORMULARIO PARA CREAR NUEVO GRUPO
    # =========================================
    st.subheader("➕ Registrar nuevo grupo")

    nombre = st.text_input("Nombre del Grupo")
    distrito = st.text_input("Distrito")
    inicio_ciclo = st.date_input("Inicio del Ciclo", value=date.today())

    if st.button("Guardar grupo"):
        if not nombre.strip():
            st.error("El nombre del grupo es obligatorio.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Grupos (nombre_grupo, distrito, inicio_ciclo) VALUES (%s, %s, %s)",
                    (nombre, distrito, inicio_ciclo)
                )
                conn.commit()
                st.success("Grupo creado correctamente.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error al crear el grupo: {e}")
            finally:
                cursor.close()
                conn.close()

    st.write("---")

    # =========================================
    # SELECCIONAR GRUPO
    # =========================================
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_grupo, nombre_grupo FROM Grupos")
        grupos = cursor.fetchall()
    except Exception as e:
        st.error(f"Error al obtener grupos: {e}")
        return

    if not grupos:
        st.info("No hay grupos registrados aún.")
        cursor.close()
        conn.close()
        return

    st.write("### ⚙️ Opciones del grupo")
    grupo_id = st.selectbox(
        "Selecciona un grupo",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x)
    )

    # =========================================
    # ELIMINAR GRUPO (CON CONFIRMACIÓN)
    # =========================================
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
                    cursor.close()
                    conn.close()
                    st.experimental_rerun()

        with col2:
            if st.button("Cancelar eliminación"):
                st.session_state["confirmar_eliminar"] = False
                st.session_state.pop("grupo_a_eliminar", None)
                st.info("Operación cancelada.")

    # =========================================
    # LISTAR MIEMBROS DEL GRUPO
    # =========================================
    try:
        cursor.execute("""
            SELECT M.id_miembro, M.nombre
            FROM Grupomiembros GM
            JOIN Miembros M ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
        """, (grupo_id,))
        miembros = cursor.fetchall()
    except Exception as e:
        st.error(f"Error al obtener miembros: {e}")
        miembros = []

    st.write("### 🧑‍🤝‍🧑 Miembros del grupo")
    if miembros:
        for m in miembros:
            col1, col2 = st.columns([15, 1])
            with col1:
                st.markdown(f"✔️ {m['nombre']}")
            with col2:
                if st.button("✖️", key=f"del_{grupo_id}_{m['id_miembro']}"):
                    try:
                        cursor.execute(
                            "DELETE FROM Grupomiembros WHERE id_grupo = %s AND id_miembro = %s",
                            (grupo_id, m['id_miembro'])
                        )
                        conn.commit()
                        st.success(f"{m['nombre']} eliminado.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar miembro: {e}")
    else:
        st.info("Este grupo no tiene miembros.")

    # =========================================
    # AGREGAR MIEMBROS AL GRUPO
    # =========================================
    st.write("### ➕ Agregar miembros")
    try:
        cursor.execute("SELECT id_miembro, nombre FROM Miembros")
        todos = cursor.fetchall()
    except Exception as e:
        st.error(f"Error al obtener miembros: {e}")
        todos = []

    ids_actuales = [m['id_miembro'] for m in miembros]
    disponibles = [m for m in todos if m['id_miembro'] not in ids_actuales]

    if disponibles:
        nuevos = st.multiselect(
            "Selecciona miembros",
            options=[m['id_miembro'] for m in disponibles],
            format_func=lambda x: next(m['nombre'] for m in disponibles if m['id_miembro'] == x)
        )
        if st.button("Agregar al grupo"):
            try:
                for nm in nuevos:
                    cursor.execute(
                        "INSERT INTO Grupomiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                        (grupo_id, nm)
                    )
                conn.commit()
                st.success("Miembros agregados correctamente.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error al agregar miembros: {e}")
    else:
        st.info("No hay más miembros disponibles.")

    cursor.close()
    conn.close()
