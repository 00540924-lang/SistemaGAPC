import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

# ------------------ CSS MODERNO ------------------
st.markdown("""
    <style>
    /* Ocultar menú y pie */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fondo */
    body {
        background-color: #0E1117;
    }

    /* Tarjeta */
    .login-card {
        background-color: #1E1E1E;
        padding: 45px 35px;
        border-radius: 20px;
        width: 420px;
        margin: auto;
        margin-top: 90px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.35);
        animation: fadeIn 1s ease-in-out;
    }

    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(-10px);}
        to {opacity: 1; transform: translateY(0);}
    }

    /* Título */
    .login-title {
        text-align: center;
        font-size: 30px;
        font-weight: bold;
        color: white;
        margin-bottom: 25px;
    }

    /* Inputs */
    .stTextInput>div>div>input {
        border-radius: 12px;
        height: 45px;
        font-size: 16px;
    }

    /* Botón */
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        border-radius: 12px;
        height: 45px;
        font-size: 17px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45A049;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ TARJETA ------------------
st.markdown("<div class='login-card'>", unsafe_allow_html=True)
st.markdown("<div class='login-title'>Inicio de sesión</div>", unsafe_allow_html=True)

usuario = st.text_input("Usuario")
password = st.text_input("Contraseña", type="password")

login = st.button("Iniciar sesión")

st.markdown("</div>", unsafe_allow_html=True)

if login:
    st.success("Procesando…")

