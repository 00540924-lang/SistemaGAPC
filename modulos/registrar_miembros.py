import streamlit as st
import mysql.connector

def registrar_miembros():
    st.title("🧍 Registro de Miembros")

    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo")
        dui = st.text_input("DUI")
        telefono = st.text_input("Telefono")
        rol = st.text_input("Rol")
        enviar = st.form_submit_button("Registrar")

    if enviar:
        try:
            conexion = mysql.connector.connect(
                host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
                user="uiazxdhtd3r8o7uv",
                password="uGjZ9MXWemv7vPsjOdA5",
                database="bzn5gsi7ken7lufcglbg"
            )
            st.success("Conexión exitosa ✅")
            cursor = conexion.cursor()

            sql = "INSERT INTO miembros (Nombre, DUI, Telefono, Rol) VALUES (%s, %s, %s, %s)"
            datos = (nombre, dui, telefono, rol)
            cursor.execute(sql, datos)
            conexion.commit()
            st.success("Miembro registrado exitosamente ✔️")

            cursor.close()
            conexion.close()

        except mysql.connector.Error as e:
            st.error(f"Error MySQL: {e}")
        except Exception as e:
            st.error(f"Error general: {e}")
