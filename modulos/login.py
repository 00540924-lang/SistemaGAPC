import streamlit as st
from modulos.config.conexion import obtener_conexion
import unicodedata

# ==========================
# Funciones auxiliares
# ==========================
def limpiar_rol(rol):
    """Normaliza y limpia el rol"""
    if rol is None:
        return ""
    rol = unicodedata.normalize('NFKD', str(rol)).encode('ASCII', 'ignore').decode()
    rol = rol.lower().strip()
    rol = "".join(c for c in rol if not unicodedata.category(c).startswith('C'))
    return rol

def verificar_usuario(usuario, contraseña):
    """Verifica usuario y contraseña en la base de datos en texto plano"""
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()
        query = """
            SELECT Usuario, Rol 
            FROM Administradores 
            WHERE Usuario = %s AND Contraseña = %s
        """
        cursor.execute(query, (usuario, contraseña))
        result = cursor.fetchone()

        if not result:
            return None

        rol_limpio = limpiar_rol(result[1])
        return {"usuario": result[0], "rol": rol_limpio}

    finally:
        try:
            con.close()
        except:
            pass

# ==========================
# Función principal login
# ==========================
def login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("modulos/assets/logo_gapc.png", width=600)
        except:
            pass

    st.markdown("""
        <h2 style='text-align: center; margin-top: -30px; color:#4C3A60;'>
            Sistema de Gestión – GAPC
        </h2>
    """, unsafe_allow_html=True)

    usuario = st.text_input("Usuario", key="login_usuario_input")
    contraseña = st.text_input("Contraseña", type="password", key="login_contraseña_input")

    if st.button("Iniciar sesión"):
        if not usuario or not contraseña:
            st.error("Ingrese usuario y contraseña.")
            return

        datos = verificar_usuario(usuario, contraseña)

        if datos:
            st.session_state["usuario"] = datos["usuario"]
            st.session_state["rol"] = datos["rol"]
            st.session_state["sesion_iniciada"] = True

            st.rerun()  # ✅ CORREGIDO: reemplazado experimental_rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

# ==========================
# Ejecutar login directo
# ==========================
if __name__ == "__main__":
    login()
