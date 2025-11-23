import mysql.connector
import streamlit as st

# ==========================
# CONEXIÓN A BASE DE DATOS
# ==========================
def get_connection():
    return mysql.connector.connect(
        host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
        user="uiazxdhtd3r8o7uv",
        password="uGjZ9MXWemv7vPsjOdA5",
        database="bzn5gsi7ken7lufcglbg"
    )

# ==========================
# MÓDULO DE CREDENCIALES
# ==========================
def pagina_credenciales():
    st.title("Registro de nuevas credenciales")

    # BOTÓN PARA VOLVER AL MENÚ
    if st.button("⬅️ Regresar al menú"):
        st.session_state["page"] = "menu"
        st.rerun()

    st.write("---")
    st.subheader("➕ Registrar nueva credencial")

    # FORMULARIO
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    rol = st.selectbox("Rol", options=["Institucional", "Promotor"])

    # BOTÓN PARA GUARDAR
    if st.button("Guardar credencial"):
        if not usuario.strip() or not contraseña.strip():
            st.error("Usuario y contraseña son obligatorios.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Administradores (usuario, contraseña, rol) VALUES (%s, %s, %s)",
                    (usuario, contraseña, rol)  # <-- guardar contraseña tal cual
                )
                conn.commit()
                st.success("Credencial registrada correctamente.")
                
                # Mantener en la misma página
                st.session_state["page"] = "credenciales"
                st.stop()

            except mysql.connector.IntegrityError:
                st.error("El usuario ya existe. Elige otro.")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                cursor.close()
                conn.close()
