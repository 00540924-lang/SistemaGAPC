import streamlit as st
from modulos.config.conexion import obtener_conexion

# ----------------------------
# FUNCION DE VERIFICACION
# ----------------------------
def verificar_usuario(Usuario, Contraseña):
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None
    else:
        st.session_state["conexion_exitosa"] = True

    try:
        cursor = con.cursor()
        query = """
            SELECT Usuario, Contraseña 
            FROM Administradores 
            WHERE Usuario = %s AND Contraseña = %s
        """
        cursor.execute(query, (Usuario, Contraseña))
        result = cursor.fetchone()
        return result[0] if result else None

    finally:
        con.close()


# ----------------------------
# INTERFAZ DE LOGIN
# ----------------------------
def login():

    # Fondo degradado + estilos
    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(135deg, #1d3557, #457b9d);
        }
        .login-box {
            background: white;
            padding: 35px;
            border-radius: 15px;
            width: 350px;
            margin: auto;
            margin-top: 80px;
            box-shadow: 0px 4px 20px rgba(0,0,0,0.25);
        }
        .title {
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            color: #1d3557;
            margin-bottom: 20px;
        }
        .login-button button {
            width: 100% !important;
            border-radius: 8px !important;
            background-color: #1d3557 !important;
            color: white !important;
            height: 45px;
            font-size: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Tarjeta del login centrada
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.markdown("<div class='title'>Iniciar Sesión</div>", unsafe_allow_html=True)

    if st.session_state.get("conexion_exitosa"):
        st.success("Conexión exitosa con la base de datos")

    Usuario = st.text_input("Usuario")
    Contraseña = st.text_input("Contraseña", type="password")

    login_button = st.button("Iniciar sesión")

    if login_button:
        tipo = verificar_usuario(Usuario, Contraseña)

        if tipo:
            st.session_state["usuario"] = Usuario
            st.session_state["tipo_usuario"] = tipo
            st.session_state["sesion_iniciada"] = True
            st.success(f"Bienvenido {Usuario} 👋")
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas.")

    st.markdown("</div>", unsafe_allow_html=True)  # Cerrar caja
