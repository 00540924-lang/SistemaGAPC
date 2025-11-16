import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

st.markdown("""
    <style>
    body {
        background-color: #0E1117;
    }

    .card {
        background: #FFFFFF10;
        backdrop-filter: blur(8px);
        padding: 40px;
        width: 390px;
        margin: 120px auto;
        border-radius: 22px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        animation: zoomIn .6s ease;
    }

    @keyframes zoomIn {
        from {opacity: 0; transform: scale(0.95);}
        to {opacity: 1; transform: scale(1);}
    }

    .title {
        color: white;
        text-align: center;
        font-size: 32px;
        font-weight: 600;
        margin-bottom: 30px;
    }

    .stTextInput>div>div>input {
        border-radius: 14px;
        padding: 8px;
        height: 45px;
        font-size: 17px;
    }

    .stButton>button {
        width: 100%;
        height: 48px;
        background: linear-gradient(90deg, #7F5AF0, #4361EE);
        color: white;
        border-radius: 14px;
        font-size: 17px;
        border: none;
        cursor: pointer;
    }

    .stButton>button:hover {
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='title'>Bienvenido</div>", unsafe_allow_html=True)

user = st.text_input("Usuario")
pwd = st.text_input("Contraseña", type="password")
login = st.button("Acceder")

st.markdown("</div>", unsafe_allow_html=True)

if login:
    st.info("Verificando credenciales…")
