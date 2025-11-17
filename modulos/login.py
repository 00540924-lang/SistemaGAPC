import streamlit as st
from modulos.config.conexion import obtener_conexion

# -------------------------------------------------
# CSS PARA CAMBIAR EL FONDO (FONDO CLARO PERSONALIZADO)
# -------------------------------------------------
st.markdown("""
<style>
/* Fondo principal */
[data-testid="stAppViewContainer"] {
    background: #F7F3FA !important;  /* Morado pastel muy claro */
}

/* Fondo del sidebar */
[data-testid="stSidebar"] {
    background: #EFE8F4 !important;
}

/* Ajustar color de los inputs */
input {
    background-color: white !important;
    color: black !important;
}

/* Texto general */
body {
    color: #2A2A2A !important;
}
</style>
""", unsafe_allow_html=True)



# -------------------------------------------------
# FUNCIÓN PARA VERIFICAR USUARIO
# -------------------------------------------------
def verificar_usuario(usuario, contraseña):
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()
        query = "SELECT Usuario FROM Administradores WHERE Usuario = %s AND Contraseña = %s"
        cursor.execute(query, (usuario, contraseña))
        result = cursor.fetchone()
        return result[0] if result else None

    finally:
        con.close()



# -------------------------------------------------
# PANTALLA DE LOGIN
# -------------------------------------------------
def login():

    # -------- LOGO CENTRADO ----------
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.write("")
    with col2:
        st.image("modulos/assets/logo_gapc.png", width=800)
    with col3:
        st.write("")

    # -------- TÍTULO ----------
    st.markdown(
        """
        <h2 style='text-align: center; margin-top: -10px; color:#4C3A60;'>
            Sistema de Gestión – GAPC
        </h2>
        """,
        unsafe_allow_html=True,
    )

    # -------- TARJETA VISUAL ----------
    st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #B7A2C8, #F7C9A4);
        padding: 15px;
        border-radius: 12px;
        color: #ffffff;
        font-size: 18px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        margin: auto;
    ">
        <b>Bienvenido</b><br>
        Ingrese sus credenciales para continuar
    </div>
    """,
    unsafe_allow_html=True,
)

    st.write("")  # Espacio

    # -------- CAMPOS ----------
    usuario = st.text_input("Usuario", key="login_usuario_input")
    contraseña = st.text_input("Contraseña", type="password", key="login_contraseña_input")

    st.write("")

    # -------- BOTÓN ----------
    if st.button("Iniciar sesión"):
        validado = verificar_usuario(usuario, contraseña)

        if validado:
            st.session_state["usuario"] = usuario
            st.session_state["sesion_iniciada"] = True
            st.success(f"Bienvenido, {usuario} 👋")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")



# -------------------------------------------------
# EJECUCIÓN LOCAL
# -------------------------------------------------
if __name__ == "__main__":
    login()
