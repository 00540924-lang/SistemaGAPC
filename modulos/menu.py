import streamlit as st

# -------------------------------------------------
# ESTILOS PERSONALIZADOS DEL MENÚ
# -------------------------------------------------
MENU_STYLE = """
<style>

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #D9C9E8, #F7E3C8);
        color: #4C3A60 !important;
    }

    /* Títulos del sidebar */
    [data-testid="stSidebar"] h2 {
        color: #4C3A60 !important;
        font-weight: bold;
        text-align: center;
    }

    /* Botones redondos */
    .round-button {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: linear-gradient(135deg, #B7A2C8, #F7C9A4);
        color: white !important;
        border: none;
        font-size: 20px;
        font-weight: bold;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.20);
        transition: 0.3s ease-in-out;
        cursor: pointer;
    }

    /* Hover */
    .round-button:hover {
        transform: scale(1.08);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
    }

    /* Centrado */
    .btn-container {
        text-align: center;
        margin-top: 25px;
    }

    /* Nombre del usuario */
    .welcome-box {
        background: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        color: #4C3A60;
        font-size: 18px;
        margin-bottom: 20px;
        box-shadow: 0px 3px 10px rgba(0,0,0,0.15);
    }

</style>
"""


# -------------------------------------------------
# FUNCIÓN DEL MENÚ PRINCIPAL
# -------------------------------------------------
def menu_principal():

    st.markdown(MENU_STYLE, unsafe_allow_html=True)

    # ---- SIDEBAR ----
    st.sidebar.markdown("## 📁 Módulos")

    st.sidebar.write("Seleccione un módulo:")

    opcion = st.sidebar.radio(
        "",
        ["Dashboard", "Usuarios", "Préstamos", "Ahorros", "Reportes", "Configuración"],
        index=0
    )

    st.sidebar.write("---")
    
    # ---- CERRAR SESIÓN ----
    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state["sesion_iniciada"] = False
        st.session_state["usuario"] = ""
        st.rerun()

    # ---- MENSAJE DE BIENVENIDA ----
    st.markdown(
        f"<div class='welcome-box'>👋 Bienvenido, <b>{st.session_state['usuario']}</b></div>",
        unsafe_allow_html=True,
    )

    # ---- TITULO DEL MODULO SELECCIONADO ----
    st.markdown(
        f"<h2 style='text-align:center; color:#4C3A60;'>{opcion}</h2>",
        unsafe_allow_html=True
    )

    # ---- BOTONES REDONDOS VISUALES ----
    st.write("")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown(
            "<div class='btn-container'>"
            "<button class='round-button'>👥<br>Usuarios</button>"
            "</div>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            "<div class='btn-container'>"
            "<button class='round-button'>💰<br>Préstamos</button>"
            "</div>",
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            "<div class='btn-container'>"
            "<button class='round-button'>📑<br>Reportes</button>"
            "</div>",
            unsafe_allow_html=True
        )

    st.write("")
    col4, col5, col6 = st.columns([1, 1, 1])

    with col4:
        st.markdown(
            "<div class='btn-container'>"
            "<button class='round-button'>📊<br>Dashboard</button>"
            "</div>",
            unsafe_allow_html=True
        )

    with col5:
        st.markdown(
            "<div class='btn-container'>"
            "<button class='round-button'>📂<br>Ahorros</button>"
            "</div>",
            unsafe_allow_html=True
        )

    with col6:
        st.markdown(
            "<div class='btn-container'>"
            "<button class='round-button'>⚙️<br>Config</button>"
            "</div>",
            unsafe_allow_html=True
        )
