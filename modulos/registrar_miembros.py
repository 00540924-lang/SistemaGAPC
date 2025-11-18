import streamlit as st
import mysql.connector

def registrar_miembros():

    st.title("🧍 Registro de Miembros")

    # FORMULARIO
    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo")
        dui = st.text_input("DUI")
        telefono = st.text_input("Teléfono")
        rol = st.text_input("Rol dentro del GAPC")

        enviar = st.form_submit_button("Registrar miembro")

    # PROCESAR FORMULARIO
    if enviar:
        try:
            conexion = mysql.connector.connect(
                host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
                user="uiazxdhtd3r8o7uv",
                password="uGjZ9MXWemv7vPsjOdA5",
                database="bzn5gsi7ken7lufcglbg"
            )
            cursor = conexion.cursor()

            sql = """
                INSERT INTO miembros (Nombre, DUI, Teléfono, Rol)
                VALUES (%s, %s, %s, %s)
            """

            datos = (nombre, dui, telefono, rol)

            cursor.execute(sql, datos)
            conexion.commit()

            st.success("✔️ Miembro registrado exitosamente")

        except mysql.connector.Error as err:
            st.error(f"❌ Error: {err}")

        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    # BOTÓN PARA VOLVER AL MENÚ
    if st.button("⬅ Volver al menú"):
        st.session_state.page = "menu"
        st.rerun()
