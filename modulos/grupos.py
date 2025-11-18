import mysql.connector
import streamlit as st

# ==========================
#  CONEXIÓN A BASE DE DATOS
# ==========================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="tu_basedatos"
    )

# ==========================
#  PÁGINA PRINCIPAL
# ==========================
def pagina_grupos():
    st.title("Gestión de Grupos")

    st.subheader("➕ Registrar nuevo grupo")

    # ---------------------------------------------
    # FORMULARIO PARA CREAR GRUPO
    # ---------------------------------------------
    nombre = st.text_input("Nombre del Grupo")
    distrito = st.text_input("Distrito")
    inicio_ciclo = st.date_input("Inicio del Ciclo")

    if st.button("Guardar grupo"):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Grupos (nombre_grupo, distrito, inicio_ciclo) VALUES (%s, %s, %s)",
            (nombre, distrito, inicio_ciclo)
        )
        conn.commit()
        st.success("Grupo registrado correctamente")

        cursor.close()
        conn.close()

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
        st.info("No hay grupos registrados aún.")
        return

    grupo_seleccionado = st.selectbox(
        "Selecciona un grupo",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x)
    )

    st.write("### Miembros del grupo")

    # ---------------------------------------------
    # OBTENER MIEMBROS DEL GRUPO
    # ---------------------------------------------
    cursor.execute("""
        SELECT M.id_miembro, M.nombre
        FROM GrupoMiembros GM
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
                if st.button("❌", key=f"del_{m['id_miembro']}"):
                    cursor.execute(
                        "DELETE FROM GrupoMiembros WHERE id_grupo = %s AND id_miembro = %s",
                        (grupo_seleccionado, m["id_miembro"])
                    )
                    conn.commit()
                    st.success(f"{m['nombre']} eliminado del grupo.")
                    st.rerun()
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

    miembros_disponibles = [m for m in todos_miembros if m["id_miembro"] not in ids_actuales]

    if miembros_disponibles:
        nuevos = st.multiselect(
            "Selecciona miembros para agregar",
            options=[m["id_miembro"] for m in miembros_disponibles],
            format_func=lambda x: next(m["nombre"] for m in miembros_disponibles if m["id_miembro"] == x)
        )

        if st.button("Agregar al grupo"):
            for id_miembro in nuevos:
                cursor.execute(
                    "INSERT INTO GrupoMiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                    (grupo_seleccionado, id_miembro)
                )
            conn.commit()
            st.success("Miembros agregados correctamente.")
            st.rerun()
    else:
        st.info("Todos los miembros ya están en este grupo.")

    cursor.close()
    conn.close()
