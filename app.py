import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

# ----------- ESTILOS -----------
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
        font-size: 30px;
        margin-bottom: 20px;
    }

    .menu-btn {
        background-color: #00B4D8;
        color: white;
        padding: 15px;
        width: 200px;
        border-radius: 12px;
        font-size: 18px;
        margin: 10px;
        border: none;
    }

    </style>
""", unsafe_allow_html=True)


# ----------- LOGIN / MENÚ LÓGICA -----------
if "logueado" not in st.session_state:
    st.session_state.logueado = False


# ================= LOGIN =================
if not st.session_state.logueado:

    st.image("https://upload.wikimedia.org/wikipedia/commons/a/ab/Logo_TV_2015.png", width=90)

    st.markdown("<div class='titulo-gagpc'>Grupos de Ahorro y Préstamo Comunitario (GAPC)</div>",
                unsafe_allow_html=True)

    st.markdown("<div class='bienvenidos'>¡Bienvenidos!</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Panel Administrativo</div>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if usuario == "admin" and password == "1234":
            st.session_state.logueado = True
            st.success("Ingreso exitoso")
        else:
            st.error("Usuario o contraseña incorrectos")

    st.markdown("</div>", unsafe_allow_html=True)


# ================= MENÚ =================
else:
    st.markdown("<h1 style='text-align:center; color:white;'>Menú Principal</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏦 Grupos", key="grupos"):
            st.session_state.pagina = "grupos"

    with col2:
        if st.button("💰 Ahorros", key="ahorros"):
            st.session_state.pagina = "ahorros"

    with col3:
        if st.button("💳 Préstamos", key="prestamos"):
            st.session_state.pagina = "prestamos"


    # --------- CONTENIDO SEGÚN BOTÓN ----------
    if "pagina" in st.session_state:

        if st.session_state.pagina == "grupos":
            st.subheader("👥 Gestión de Grupos")
            st.write("Aquí irá la administración de los grupos.")

        elif st.session_state.pagina == "ahorros":
            st.subheader("💰 Gestión de Ahorros")
            st.write("Aquí irá el módulo de ahorros.")

        elif st.session_state.pagina == "prestamos":
            st.subheader("💳 Gestión de Préstamos")
            st.write("Aquí irá el módulo de préstamos.")

