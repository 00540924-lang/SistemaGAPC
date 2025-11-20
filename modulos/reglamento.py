import streamlit as st
import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    return mysql.connector.connect(
        host="containers-us-west-115.railway.app",
        user="root",
        password="EYmbgBSmzxYJuFOkquBG",
        database="railway",
        port=7474
    )

def mostrar_reglamento():

    # ============================
    # 1️⃣ Variables desde sesión
    # ============================
    id_grupo = st.session_state.get("id_grupo")
    nombre_grupo = st.session_state.get("nombre_grupo", "No definido")

    if not id_grupo:
        st.error("Error: No se encontró el grupo del usuario en la sesión.")
        return

    # ============================
    # 2️⃣ Título dinámico
    # ============================
    st.title(f"📘 Reglamento interno del grupo {nombre_grupo}")

    # ============================
    # 3️⃣ Conexion
    # ============================
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
    except Error as e:
        st.error(f"❌ Error al conectar a la base de datos: {e}")
        return

    # ============================
    # 4️⃣ Ver si el grupo ya tiene reglamento
    # ============================
    cursor.execute("SELECT * FROM Reglamento WHERE id_grupo = %s", (id_grupo,))
    resultado = cursor.fetchone()

    # ============================
    # 5️⃣ Si NO existe → crear
    # ============================
    if not resultado:
        st.info("Este grupo aún no tiene reglamento registrado.")

        contenido_nuevo = st.text_area("Escriba el reglamento del grupo:")

        if st.button("Guardar reglamento"):
            cursor.execute(
                "INSERT INTO Reglamento (id_grupo, contenido) VALUES (%s, %s)",
                (id_grupo, contenido_nuevo)
            )
            conexion.commit()
            st.success("Reglamento agregado correctamente.")
            st.rerun()

    else:
        # ============================
        # 6️⃣ Si existe → mostrar y permitir editar
        # ============================
        st.subheader("Reglamento actual:")

        contenido_editado = st.text_area(
            "Puede editar el reglamento:",
            value=resultado["contenido"],
            height=300
        )

        if st.button("Guardar cambios"):
            cursor.execute(
                "UPDATE Reglamento SET contenido = %s WHERE id_grupo = %s",
                (contenido_editado, id_grupo)
            )
            conexion.commit()
            st.success("Reglamento actualizado correctamente.")
            st.rerun()

    cursor.close()
    conexion.close()

