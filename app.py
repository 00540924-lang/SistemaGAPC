import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #141E30, #243B55);
        height: 100vh;
    }

    /* Contenedor principal estilo vidrio */
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

    /* Título GAPC debajo del logo */
    .titulo-gagpc {
        font-size: 26px;
        color: #ffffff;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 25px;
        font-weight: 600;
    }

    .title {
        color: #FFFFFF;
        text-align: center;
        font-size: 30px;
        margin-bottom: 20px;
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
    }

    .stButton>button:hover {
        background-color: #0096C7;
    }
    </style>
""", unsafe_allow_html=True)

# --- Logo ---
st.image("https://upload.wikimedia.org/wikipedia/commons/a/ab/Logo_TV_2015.png", width=90)

# --- Título debajo del logo ---
st.markdown("<div class='titulo-gagpc'>Grupos de Ahorro y Préstamo Comunitario (GAPC)</div>",
            unsafe_allow_html=True)

u = st.text_input("Usuario")
p = st.text_input("Contraseña", type="password")

if st.button("Ingresar"):
    st.success("Bienvenido!")

st.markdown("</div>", unsafe_allow_html=True)

