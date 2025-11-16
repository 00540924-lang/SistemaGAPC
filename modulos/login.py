import streamlit as st
import base64

st.set_page_config(page_title="GAPC - Login", layout="centered")

# --- LOGO BASE64 ---
logo_base64 = """
iVBORw0KGgoAAAANSUhEUgAAA... (recortado para este mensaje)
"""

logo_html = f"""
<img src="data:image/png;base64,{logo_base64}" width="200">
"""

# ---- ESTILOS CSS ----
st.markdown("""
<style>

body {
    background: linear-gradient(135deg, #B7A2C6 0%, #F4C9A9 100%);
}

/* Caja del login */
.login-box {
    background: #FFF7F2;
    padding: 40px;
    width: 400px;
    margin: auto;
    margin-top: 90px;
    border-radius: 20px;
    box-shadow: 0px 10px 35px rgba(0,0,0,0.15);
    text-align: center;
}

/* Título */
.login-title {
    font-size: 30px;
    font-weight: 900;
    color: #2D2B2F;
    margin-top: 10px;
}

/* Inputs */
input {
    border-radius: 10px !important;
}

/* Botón */
.stButton>button {
    background-color: #9A86AE;
    color: white;
    width: 100%;
    padding: 12px;
    border-radius: 12px;
    font-size: 18px;
    border: none;
    transition: 0.2s ease;
}

.stButton>button:hover {
    background-color: #7D6A94;
}

/* Slogan */
.slogan {
    color: #F5B995;
    font-weight: 700;
    font-size: 16px;
    margin-top: -10px;
}

</style>
""", unsafe_allow_html=True)

# ---- INTERFAZ ----
st.markdown("<div class='login-box'>", unsafe_allow_html=True)

st.markdown(logo_html, unsafe_allow_html=True)

st.markdown("<div class='login-title'>GAPC</div>", unsafe_allow_html=True)
st.markdown("<div class='slogan'>Ahorra, Crece, Juntos</div>", unsafe_allow_html=True)

email = st.text_input("Correo electrónico")
password = st.text_input("Contraseña", type="password")

st.button("Iniciar sesión")

st.markdown("</div>", unsafe_allow_html=True)
