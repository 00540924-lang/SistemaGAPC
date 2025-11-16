import streamlit as st
from modulos.config.conexion import obtener_conexion

# -----------------------------------------
# VERIFICAR USUARIO (tu función original)
# -----------------------------------------
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


# -----------------------------------------
# DISEÑO MODERNO LOGIN
# -----------------------------------------
def login():

    st.set_page_config(page_title="Login", layout="centered")

    # ------------------- CSS SUPER PREMIUM -------------------
    st.markdown("""
        <style>

        /* Fondo degradado suave animado */
        body {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            background-size: 400% 400%;
            animation: gradientMove 12s ease infinite;
        }

        @keyframes gradientMove {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        /* Contenedor Glassmorphism */
        .glass-box {
            margin-top: 90px;
            width: 420px;
            padding: 40px;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.12);
            box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-left: auto;
            margin-right: auto;
            text-align: center;
        }

        /* Título */
        .title {
            font-size: 32px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 10px;
        }

        /* Subtítulo */
        .subtitle {
            font-size: 16px;
            color: #dff1ff;
            margin-bottom: 25px;
        }

        /* Inputs */
        .stTextInput>div>div>input {
            background: rgba(255,255,255,0.25) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,0.3) !important;
            color: white !important;
            height: 45px;
        }

        /* Texto dentro del input */
        ::placeholder {
            color: white !important;
        }

        /* Botón */
        .stButton>button {
            width: 100%;
            height: 48px;
            border-radius: 12px;
            background: linear-gradient(135deg, #00d2ff, #3a7bd5);
            border: none;
            color: white;
            font-size: 18px;
            font-weight: 600;
            transition: 0.3s ease;
        }

        /* Hover botón */
        .stButton>button:hover {
            background: linear-gradient(135deg, #3a7bd5, #00d2ff);
            transform: translateY(-2px);
            box-shadow: 0px 6px 18px rgba(0,0,0,0.3);
        }

        </style>
    """, unsafe_allow_html=True)

    # ---------- Caja principal ----------
    st.markdown("<div class='glass-box'>", unsafe_allow_html=True)

    st.markdown("<div class='title'>Bienvenido</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Inicie sesión para continuar</div>", unsafe_allow_html=True)

    if st.session_state.get("conexion_exitosa"):
        st.success("Conexión establecida correctamente ✔")

    Usuario = st.text_input("Usuario")
    Contraseña = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión"):
        tipo = verificar_usuario(Usuario, Contraseña)

        if tipo:
            st.session_state["usuario"] = Usuario
            st.session_state["tipo_usuario"] = tipo
            st.session_state["sesion_iniciada"] = True
            st.success(f"Bienvenido {Usuario} 👋")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

    st.markdown("</div>", unsafe_allow_html=True)  # Cierra el div del login
