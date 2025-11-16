import streamlit as st
from modulos.config.conexion import obtener_conexion

# ==========================
#  FUNCIÓN PARA VALIDAR USUARIO
# ==========================
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
            SELECT Usuario 
            FROM Administradores 
            WHERE Usuario = %s AND `Contraseña` = %s
        """
        cursor.execute(query, (Usuario, Contraseña))
        result = cursor.fetchone()

        return result[0] if result else None

    finally:
        con.close()


# ==========================
#  INTERFAZ DE LOGIN DISEÑADA
# ==========================
def login():

    st.set_page_config(page_title="Login", layout="centered")

    # ------- ESTILOS CSS -------
    st.markdown("""
        <style>

        /* Fondo degradado */
        body {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            height: 100vh;
        }

        /* Caja principal de login */
        .glass-card {
            background: rgba(255, 255, 255, 0.10);
            backdrop-filter: blur(12px);
            padding: 40px;
            width: 420px;
            margin: 40px auto;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.20);
            text-align: center;
            animation: fadeIn 0.9s ease-in-out;
        }

        /* Animación */
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(-10px);}
            to {opacity: 1; transform: translateY(0);}
        }

        /* Título */
        .titulo {
            font-size: 26px;
            color: #FFFFFF;
            margin-bottom: 10px;
            font-weight: 600;
        }

        /* Subtítulo */
        .sub {
            font-size: 17px;
            color: #cfe9ff;
            margin-bottom: 25px;
        }

        /* Input */
        .stTextInput>div>div>input {
            border-radius: 10px;
            height: 45px;
        }

        /* Botón */
        .stButton>button {
            width: 100%;
            height: 45px;
            background-color: #00B4D8;
            border-radius: 10px;
            font-size: 18px;
            border: none;
            color: white;
        }
        .stButton>button:hover {
            background-color: #0096C7;
            transform: scale(1.02);
        }

        </style>
    """, unsafe_allow_html=True)

    # ------- INTERFAZ VISUAL -------
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    st.markdown("<div class='titulo'>Inicio de Sesión</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>Acceda al Panel Administrativo</div>", unsafe_allow_html=True)

    # Mostrar mensaje si la conexión fue exitosa
    if st.session_state.get("conexion_exitosa"):
        st.success("Conexión a la base de datos exitosa.")

    Usuario = st.text_input("Usuario", key="login_usuario_input")
    Contraseña = st.text_input("Contraseña", type="password", key="login_contraseña_input")

    if st.button("Ingresar"):
        usuario_validado = verificar_usuario(Usuario, Contraseña)

        if usuario_validado:
            st.session_state["usuario"] = usuario_validado
            st.session_state["sesion_iniciada"] = True
            st.success(f"Bienvenido {usuario_validado} 👋")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

    st.markdown("</div>", unsafe_allow_html=True)
