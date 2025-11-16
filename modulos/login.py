import streamlit as st
from modulos.config.conexion import obtener_conexion

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


def login():
    st.set_page_config(page_title="GAPC Login", layout="centered")

    # --- ESTILOS BONITOS ---
    st.markdown("""
        <style>
        body {
            background: linear-gradient(135deg, #141E30, #243B55);
            height: 100vh;
        }

        .glass {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px);
            padding: 40px;
            width: 430px;
            margin: 20px auto;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            animation: slideDown .8s ease;
        }

        @keyframes slideDown {
            from {opacity: 0; transform: translateY(-15px);}
            to {opacity: 1; transform: translateY(0);}
        }

        .titulo-gagpc {
            font-size: 26px;
            color: #ffffff;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 5px;
            font-weight: 600;
        }

        .bienvenidos {
            font-size: 18px;
            color: #dfefff;
            text-align: center;
            margin-bottom: 25px;
            font-weight: 400;
        }

        .title {
            color: #FFFFFF;
            text-align: center;
            font-size: 28px;
            margin-bottom: 20px;
            font-weight: 600;
        }

        .stTextInput>div>div>input {
            border-radius: 10px;
            height: 45px;
        }

        .stButton>button {
            width: 100%;
            height: 45px;
            background-color: #00B4D8;
            border-radius: 10px;
            font-size: 17px;
            border: none;
            color: white;
            cursor: pointer;
        }

        .stButton>button:hover {
            background-color: #0096C7;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- LOGO ---
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/ab/Logo_TV_2015.png", width=90)

    # --- TÍTULO ---
    st.markdown("<div class='titulo-gagpc'>Grupos de Ahorro y Préstamo Comunitario (GAPC)</div>",
                unsafe_allow_html=True)

    # --- SUBTÍTULO ---
    st.markdown("<div class='bienvenidos'>¡Bienvenidos!</div>", unsafe_allow_html=True)


    st.markdown("<div class='title'>Iniciar Sesión</div>", unsafe_allow_html=True)

    # --- Inputs reales de tu login ---
    Usuario = st.text_input("Usuario", key="login_usuario_input")
    Contraseña = st.text_input("Contraseña", type="password", key="login_contraseña_input")

    # --- Botón ---
    if st.button("Iniciar sesión"):
        tipo = verificar_usuario(Usuario, Contraseña)
        if tipo:
            st.session_state["usuario"] = Usuario
            st.session_state["tipo_usuario"] = tipo
            st.session_state["sesion_iniciada"] = True
            st.success(f"Bienvenido ({Usuario}) 👋")
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas.")

    st.markdown("</div>", unsafe_allow_html=True)
