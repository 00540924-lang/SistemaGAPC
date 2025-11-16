import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

# ---------- ESTILOS ----------
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
        font-weight: 600;
    }
    .bienvenidos {
        font-size: 18px;
        color: #dfefff;
        text-align: center;
        margin-bottom: 25px;
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

# ---------- LOGO ----------
st.image("https://upload.wikimedia.org/wikipedia/commons/a/ab/Logo_TV_2015.png", width=90)

# ---------- TITULOS ----------
st.markdown("<div class='titulo-gagpc'>Grupos de Ahorro y Préstamo Comunitario (GAPC)</div>", unsafe_allow_html=True)
st.markdown("<div class='bienvenidos'>¡Bienvenidos!</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# SISTEMA DE LOGIN
# -------------------------------------------------------------------

# Usuario y contraseña válidos
USER = "Dark"
PASS = "Valorant"

# Session state para recordar si ya inició sesión
if "logueado" not in st.session_state:
    st.session_state.logueado = False

# Si NO está logueado → mostrar login
if not st.session_state.logueado:

    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Panel Administrativo</div>", unsafe_allow_html=True)

    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if u == USER and p == PASS:
            st.session_state.logueado = True
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas")

    st.markdown("</div>", unsafe_allow_html=True)

# Si ya inició sesión → mostrar menú
else:
    st.success("✔ Sesión iniciada correctamente")
    st.markdown("### Menú Principal")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📁 Gestión de Grupos"):
            st.info("Abriste Gestión de Grupos")

    with col2:
        if st.button("💳 Registro de Aportes"):
            st.info("Abriste Registro de Aportes")

    if st.button("🚪 Cerrar sesión"):
        st.session_state.logueado = False
        st.rerun()

