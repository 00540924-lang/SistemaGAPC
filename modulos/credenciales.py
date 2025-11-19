import mysql.connector
import streamlit as st
import hashlib

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
    st.title("Registro de Credenciales de Directiva")

    # BOTÓN PARA VOLVER AL MENÚ
    if st.button("⬅️ Regresar al menú"):
        st.session_state["page"] = "menu"
        st.experimental_rerun()

    st.write("---")

    st.subheader("➕ Registrar nueva credencial")

    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    rol = st.selectbox("Rol", options=["Institucional", "Promotor", "Miembro"])

    # Opcional: seleccionar grupo al que pertenece el admin
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_grupo, nombre_grupo FROM Grupos")
        grupos = cursor.fetchall()
        cursor.close()
        conn.close()
    except:
        grupos = []

    id_grupo = None
    if grupos:
        id_grupo = st.selectbox(
            "Asignar a grupo",
            options=[g["id_grupo"] for g in grupos],
            format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x)
        )

    if st.button("Guardar credencial"):
        if not usuario.strip() or not contraseña.strip():
            st.error("Usuario y contraseña son obligatorios.")
        else:
            # encriptar contraseña usando SHA256
            hash_password = hashlib.sha256(contraseña.encode()).hexdigest()

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Administradores (usuario, contraseña, rol, id_grupo) VALUES (%s, %s, %s, %s)",
                    (usuario, hash_password, rol, id_grupo)
                )
                conn.commit()
                st.success("Credencial registrada correctamente.")
                st.experimental_rerun()
            except mysql.connector.IntegrityError:
                st.error("El usuario ya existe. Elige otro.")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                cursor.close()
                conn.close()
