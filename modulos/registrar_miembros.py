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

            sql = "INSERT INTO miembros (Nombre, DUI, Telefono) VALUES (%s, %s, %s)"
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

    # ------------------ BOTÓN REGRESAR ------------------
    st.write("")  # espaciado
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    # ------------------ TABLA DE MIEMBROS ------------------
    try:
        conexion = mysql.connector.connect(
            host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
            user="uiazxdhtd3r8o7uv",
            password="uGjZ9MXWemv7vPsjOdA5",
            database="bzn5gsi7ken7lufcglbg"
        )
        cursor = conexion.cursor()
        cursor.execute("SELECT id_miembros, Nombre, DUI, Telefono FROM miembros")
        miembros = cursor.fetchall()

        if miembros:
            # Crear DataFrame y renombrar columnas
            df = pd.DataFrame(miembros, columns=["No.", "Nombre", "DUI", "Teléfono"])
            df.index = df.index + 1  # numeración desde 1

            # Convertir a HTML con clase para CSS
            html = df.to_html(classes="miembros-table", index=False)

            # Mostrar tabla centrada con encabezados centrados
            st.markdown(
                f"""
                <style>
                    .miembros-table th {{
                        text-align: center;
                        background-color: #f0f0f0;
                        padding: 8px;
                    }}
                    .miembros-table td {{
                        text-align: center;
                        padding: 8px;
                    }}
                    .miembros-table {{
                        width: 80%;
                        margin-left: auto;
                        margin-right: auto;
                        border-collapse: collapse;
                    }}
                </style>
                <h3 style="text-align:center;">Miembros Registrados</h3>
                {html}
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("No hay miembros registrados aún.")

        cursor.close()
        conexion.close()

    except mysql.connector.Error as e:
        st.error(f"Error MySQL al mostrar miembros: {e}")
    except Exception as e:
        st.error(f"Error general al mostrar miembros: {e}")
