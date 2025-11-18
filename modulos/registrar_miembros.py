import streamlit as st
import mysql.connector
import pandas as pd

def registrar_miembros():
    st.title("🧍 Registro de Miembros")

    # ------------------ FORMULARIO ------------------
    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo")
        dui = st.text_input("DUI")
        telefono = st.text_input("Teléfono")
        enviar = st.form_submit_button("Registrar")

    # ------------------ PROCESAR FORMULARIO ------------------
    if enviar:
        try:
            conexion = mysql.connector.connect(
                host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
                user="uiazxdhtd3r8o7uv",
                password="uGjZ9MXWemv7vPsjOdA5",
                database="bzn5gsi7ken7lufcglbg"
            )

            cursor = conexion.cursor()
            sql = "INSERT INTO Miembros (Nombre, DUI, Telefono) VALUES (%s, %s, %s)"
            datos = (nombre, dui, telefono)
            cursor.execute(sql, datos)
            conexion.commit()
            st.success("Miembro registrado exitosamente ✔️")

            cursor.close()
            conexion.close()

        except mysql.connector.Error as e:
            st.error(f"Error MySQL: {e}")
        except Exception as e:
            st.error(f"Error general: {e}")

    # ------------------ LISTA DE MIEMBROS ------------------
    st.markdown("### 📋 Miembros registrados")
    try:
        conexion = mysql.connector.connect(
            host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
            user="uiazxdhtd3r8o7uv",
            password="uGjZ9MXWemv7vPsjOdA5",
            database="bzn5gsi7ken7lufcglbg"
        )
        cursor = conexion.cursor()
        cursor.execute("SELECT Nombre, DUI, Telefono FROM Miembros")
        resultados = cursor.fetchall()

        if resultados:
            # Crear DataFrame con encabezados y numeración
            df = pd.DataFrame(resultados, columns=["Nombre", "DUI", "Teléfono"])
            df.index = range(1, len(df) + 1)
            df.index.name = "No."
            st.table(df)
        else:
            st.info("No hay miembros registrados aún.")

        cursor.close()
        conexion.close()
    except mysql.connector.Error as e:
        st.error(f"Error MySQL: {e}")
    except Exception as e:
        st.error(f"Error general: {e}")

    # ------------------ BOTÓN REGRESAR ------------------
    st.write("")  # espaciado
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
