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
# FUNCIÓN PARA VERIFICAR USUARIO EXISTENTE
# ==========================
def usuario_existe(usuario):
    """Verifica si el usuario ya existe en la base de datos"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM Administradores WHERE Usuario = %s",  # ✅ MAYÚSCULA
            (usuario,)
        )
        resultado = cursor.fetchone()
        return resultado[0] > 0
    except Exception as e:
        st.error(f"Error al verificar usuario: {e}")
        return True  # Por seguridad, asumimos que existe si hay error
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

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
    usuario = st.text_input("Usuario").strip()
    contraseña = st.text_input("Contraseña", type="password")
    rol = st.selectbox("Rol", options=["Institucional", "Promotor"])

    # BOTÓN PARA GUARDAR
    if st.button("Guardar credencial"):
        # VALIDACIONES
        if not usuario:
            st.error("El usuario es obligatorio.")
        elif not contraseña.strip():
            st.error("La contraseña es obligatoria.")
        elif len(contraseña) < 4:
            st.error("La contraseña debe tener al menos 4 caracteres.")
        elif usuario_existe(usuario):
            st.error("❌ El usuario ya existe. Por favor, elige otro nombre de usuario.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # INSERTAR NUEVO USUARIO (✅ NOMBRES CORREGIDOS)
                cursor.execute(
                    "INSERT INTO Administradores (Usuario, Contraseña, Rol) VALUES (%s, %s, %s)",
                    (usuario, contraseña, rol)
                )
                conn.commit()
                
                st.success("✅ Credencial registrada correctamente.")
                
                # Limpiar formulario
                st.session_state["credencial_form_cleared"] = True
                
            except mysql.connector.IntegrityError as e:
                # Esta excepción captura violaciones de UNIQUE KEY/PRIMARY KEY
                if "Duplicate entry" in str(e):
                    st.error("❌ Error: El usuario ya existe en la base de datos.")
                else:
                    st.error(f"❌ Error de integridad: {e}")
            except Exception as e:
                st.error(f"❌ Error inesperado: {e}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

    # Limpiar campos después de guardar exitosamente
    if st.session_state.get("credencial_form_cleared", False):
        st.session_state["credencial_form_cleared"] = False
        st.rerun()

# ==========================
# FUNCIÓN ADICIONAL: LISTAR USUARIOS EXISTENTES
# ==========================
def mostrar_usuarios_existentes():
    """Función opcional para mostrar usuarios existentes (puedes agregarla al menú)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Usuario, Rol FROM Administradores ORDER BY Usuario")  # ✅ MAYÚSCULAS
        usuarios = cursor.fetchall()
        
        if usuarios:
            st.subheader("👥 Usuarios existentes")
            for usuario, rol in usuarios:
                st.write(f"- **{usuario}** ({rol})")
        else:
            st.info("No hay usuarios registrados.")
            
    except Exception as e:
        st.error(f"Error al cargar usuarios: {e}")
    finally:
        cursor.close()
        conn.close()
