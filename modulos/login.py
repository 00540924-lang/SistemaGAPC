import streamlit as st
from modulos.config.conexion import obtener_conexion


# -------------------------------------------------
# FUNCIÓN PARA VERIFICAR USUARIO EN LA BASE DE DATOS
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

    # ---------- LOGO CENTRADO ----------
    st.markdown(
        """
        <div style="display: flex; justify-content: center; margin-top: -40px;">
            <img src="modulos/assets/logo_gapc.png" width="350">
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- TÍTULO ----------
    st.markdown(
        """
        <h2 style='text-align: center; margin-top: -10px;'>
            Sistema de Gestión – GAPC
        </h2>
        """,
        unsafe_allow_html=True,
    )

    # ---------- TARJETA DE BIENVENIDA ----------
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #3085C3, #FEEAA1);
            padding: 25px;
            border-radius: 12px;
            color: white;
            font-size: 16px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
        ">
            <b>Bienvenido</b><br>
            Ingrese sus credenciales para continuar.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    # ---------- CAMPOS ----------
    usuario = st.text_input("Usuario", key="login_usuario_input")
    contraseña = st.text_input("Contraseña", type="password", key="login_contraseña_input")

    st.write("")

    # ---------- BOTÓN ----------
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
# EJECUCIÓN LOCAL PARA PRUEBA
# -------------------------------------------------
if __name__ == "__main__":
    login()
