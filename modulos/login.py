import streamlit as st
from modulos.config.conexion import obtener_conexion
import unicodedata

# -------------------------------------------------
# Función para normalizar/limpiar el rol
# -------------------------------------------------
def limpiar_rol(rol):
    if rol is None:
        return ""
    # Normaliza tildes (institución → institucion)
    rol = unicodedata.normalize('NFKD', str(rol)).encode('ASCII', 'ignore').decode()
    # Minúsculas y strip
    rol = rol.lower().strip()
    # Remueve caracteres de control invisibles
    rol = "".join(c for c in rol if not unicodedata.category(c).startswith('C'))
    return rol

# -------------------------------------------------
# FUNCIÓN PARA VERIFICAR USUARIO + ROL
# -------------------------------------------------
def verificar_usuario(usuario, contraseña):
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

        # DEBUG opcional: ver valor crudo desde BD (descomentar si es necesario)
        # st.write("DEBUG - Rol crudo desde BD:", repr(result[1]))

        rol_limpio = limpiar_rol(result[1])

        return {
            "usuario": result[0],
            "rol": rol_limpio
        }

    finally:
        try:
            con.close()
        except:
            pass

# -------------------------------------------------
# PANTALLA DE LOGIN
# -------------------------------------------------
def login():

    # Logo y título
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Si no tienes el logo, coméntalo o pon otra ruta
        try:
            st.image("modulos/assets/logo_gapc.png", width=600)
        except:
            pass

    st.markdown(
        """
        <h2 style='text-align: center; margin-top: -30px; color:#4C3A60;'>
            Sistema de Gestión – GAPC
        </h2>
        """,
        unsafe_allow_html=True,
    )

    # Campos de entrada
    usuario = st.text_input("Usuario", key="login_usuario_input")
    contraseña = st.text_input("Contraseña", type="password", key="login_contraseña_input")

    # Botón de inicio
    if st.button("Iniciar sesión"):
        # Validaciones básicas
        if not usuario or not contraseña:
            st.error("Ingrese usuario y contraseña.")
            return

        datos = verificar_usuario(usuario, contraseña)

        if datos:
            # Guardar en session_state exactamente las claves que usa app.py
            st.session_state["usuario"] = datos["usuario"]
            st.session_state["rol"] = datos["rol"]            # rol ya viene limpio y en minúsculas
            st.session_state["sesion_iniciada"] = True

            st.success(f"Bienvenido {datos['usuario']} 👋 (Rol: {datos['rol']})")
            st.experimental_rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

# -------------------------------------------------
# EJECUCIÓN DIRECTA (solo si ejecutas este archivo)
# -------------------------------------------------
if __name__ == "__main__":
    login()


