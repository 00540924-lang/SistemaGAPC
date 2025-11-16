import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

# ------------------ CSS 100% SEGURO ------------------
css = '''
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

body {
    background: linear-gradient(160deg, #0D0D0D 0%, #1A1A1A 40%, #2A2A2A 100%);
    color: #FFFFFF;
    font-family: Arial, sans-serif;
}

.mobile-card {
    background: #111111;
    width: 90%;
    max-width: 380px;
    margin: 80px auto;
    padding: 35px 25px;
    border-radius: 28px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.6);
}

.mobile-title {
    font-size: 28px;
    text-align: center;
    font-weight: bold;
    margin-bottom: 30px;
    color: #FFFFFF;
}

.stTextInput>div>div>input {
    border-radius: 14px;
    height: 50px;
    font-size: 17px;
    padding-left: 15px;
    color: white;
    background-color: #1E1E1E;
    border: 1px solid #333333;
}

.stButton>button {
    width: 100%;
    height: 55px;
    background: #4CAF50;
    color: white;
    border-radius: 14px;
    font-size: 18px;
    border: none;
    margin-top: 10px;
    font-weight: bold;
}

.stButton>button:hover {
    background: #45A049;
}

.small-text {
    text-align: center;
    margin-top: 20px;
    color: #BBBBBB;
    font-size: 13px;
}
</style>
'''

st.markdown(css, unsafe_allow_html=True)

# ------------------ TARJETA ------------------
st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
st.markdown("<div class='mobile-title'>Iniciar sesión</div>", unsafe_allow_html=True)

usuario = st.text_input("Usuario")
password = st.text_input("Contraseña", type="password")

if st.button("Ingresar"):
    st.success("Validando información…")

st.markdown("<div class='small-text'>© 2024 - Tu Sistema</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
