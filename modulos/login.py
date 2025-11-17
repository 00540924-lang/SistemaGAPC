import streamlit as st
from modulos.config.conexion import obtener_conexion

# -------------------------------------------------
# CSS PARA CAMBIAR EL FONDO (FONDO CLARO PERSONALIZADO)
# -------------------------------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: #F7F3FA !important;
}
[data-testid="stSidebar"] {
    background: #EFE8F4 !important;
}
input {
    background-color: white !important;
    color: black !important;
}
body {
    color: #2A2A2A !important;
}
</style>
""", unsafe_allow_html=True)

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

        rol_limpio = result[1].strip().lower()   # ←←← AQUI ESTA LA CLAVE

        return {
            "usuario": result[0],
            "rol": rol_limpio
        }

    finally:
        con.close()

# -------------------------------------------------
# PANTALLA DE LOGIN
# -------------------------------------------------
def login():

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("modulos/assets/logo_gapc.png", width=800)

    st.markdown(
        """
        <h2 style='text-align: center; margin-top: -30px; color:#4C3A60;'>
            Sistema de Gestión – GAPC
        </h2>
        """,
        unsafe_allow_html=True,
    )

    usuario = st.text_input("Usuario", key="login_usuario_input")
    contraseña = st.text_input("Contraseña", type="password", key="login_contraseña_input")

    if st.button("Iniciar sesión"):
        datos = verificar_usuario(usuario, contraseña)

        if datos:
            st.session_state["usuario"] = datos["usuario"]
            st.session_state["rol"] = datos["rol"]  # ← YA VIENE LIMPIO Y EN MINÚSCULAS
            st.session_state["sesion_iniciada"] = True

            st.success(f"Bienvenido {datos['usuario']} 👋 (Rol: {datos['rol']})")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

if __name__ == "__main__":
    login()

