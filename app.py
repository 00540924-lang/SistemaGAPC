import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

# ---- CSS como lista de líneas (sin triple quotes para evitar errores) ----
css_lines = [
    "<style>",
    "body {",
    "    background: linear-gradient(135deg, #141E30, #243B55);",
    "    height: 100vh;",
    "}",
    "",
    ".glass {",
    "    background: rgba(255, 255, 255, 0.08);",
    "    backdrop-filter: blur(12px);",
    "    padding: 40px;",
    "    width: 430px;",
    "    margin: 20px auto;",
    "    border-radius: 20px;",
    "    border: 1px solid rgba(255, 255, 255, 0.15);",
    "    animation: slideDown .8s ease;",
    "}",
    "",
    "@keyframes slideDown {",
    "    from {opacity: 0; transform: translateY(-15px);}",
    "    to {opacity: 1; transform: translateY(0);}",
    "}",
    "",
    ".titulo-gagpc {",
    "    font-size: 22px;",
    "    color: #ffffff;",
    "    text-align: center;",
    "    margin-top: 10px;",
    "    margin-bottom: 6px;",
    "    font-weight: 700;",
    "}",
    "",
    ".subtitulo {",
    "    font-size: 16px;",
    "    color: #DFEFFF;",
    "    text-align: center;",
    "    margin-bottom: 18px;",
    "    font-weight: 500;",
    "}",
    "",
    ".title {",
    "    color: #FFFFFF;",
    "    text-align: center;",
    "    font-size: 28px;",
    "    margin-bottom: 20px;",
    "}",
    "",
    ".stTextInput>div>div>input {",
    "    border-radius: 10px;",
    "    height: 45px;",
    "}",
    "",
    ".stButton>button {",
    "    width: 100%;",
    "    height: 45px;",
    "    background-color: #00B4D8;",
    "    border-radius: 10px;",
    "    font-size: 17px;",
    "    border: none;",
    "    color: white;",
    "}",
    ".stButton>button:hover {",
    "    background-color: #0096C7;",
    "}",
    "</style>"
]

css = "\n".join(css_lines)
st.markdown(css, unsafe_allow_html=True)

# ---- Logo (cambia la URL por la de tu imagen RAW de GitHub si la tienes) ----
st.image("https://upload.wikimedia.org/wikipedia/commons/a/ab/Logo_TV_2015.png", width=90)

# ---- Título y subtítulo (debajo del logo) ----
st.markdown("<div class='titulo-gagpc'>Grupos de Ahorro y Préstamo Comunitario (GAPC)</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Bienvenidos!</div>", unsafe_allow_html=True)

# ---- Panel (único .glass que contiene el formulario) ----
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.markdown("<div class='title'>Panel Administrativo</div>", unsafe_allow_html=True)

usuario = st.text_input("Usuario")
password = st.tex


