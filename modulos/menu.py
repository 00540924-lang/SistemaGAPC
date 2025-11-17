import streamlit as st

def mostrar_menu():
    st.set_page_config(page_title="Panel Principal", layout="wide")

    # ---- SIDEBAR ----
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/9131/9131529.png", width=120)
        st.title("GAPC")
        st.subheader("📌 Panel Principal")

        if st.button("🔓 Cerrar sesión"):
            st.session_state["logged"] = False
            st.rerun()

    # ---- TÍTULO ----
    st.markdown(
        """
        <h1 style="text-align:center; color:#3085C3;">
            🌟 Bienvenido al Sistema GAPC
        </h1>
        <p style="text-align:center; color:gray; font-size:18px;">
            Selecciona un módulo para continuar
        </p>
        """,
        unsafe_allow_html=True
    )

    # ---- ESTILOS CSS PARA BOTONES REDONDOS ----
    st.markdown(
        """
        <style>
        .menu-btn {
            background-color: #3085C3;
            color: white;
            padding: 20px;
            border-radius: 50px;
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            margin: 10px;
            cursor: pointer;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
            transition: 0.3s;
        }
        .menu-btn:hover {
            transform: scale(1.05);
            background-color: #256a9e;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---- BOTONES REDONDOS DEL MENÚ ----
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.markdown("<div class='menu-btn'>👤 Usuarios</div>", unsafe_allow_html=True):
            pass

    with col2:
        if st.markdown("<div class='menu-btn'>📁 Expedientes</div>", unsafe_allow_html=True):
            pass

    with col3:
        if st.markdown("<div class='menu-btn'>📊 Reportes</div>", unsafe_allow_html=True):
            pass
