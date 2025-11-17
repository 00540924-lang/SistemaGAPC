import streamlit as st
from streamlit_extras.card import card
from streamlit_extras add_vertical_space import add_vertical_space
from streamlit_extras.let_it_rain import rain
from PIL import Image


# ================================
#       MENÚ PRINCIPAL PRO
# ================================
def mostrar_menu():

    st.markdown(
        """
        <h1 style='text-align: center; color:#3085C3;'>
            Panel Principal – GAPC
        </h1>
        <p style='text-align: center; font-size:18px;'>
            Seleccione un módulo para continuar
        </p>
        """,
        unsafe_allow_html=True
    )

    # --- DISEÑO EN TARJETAS ---
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📁 Gestión de Proyectos", use_container_width=True):
            st.session_state["modulo"] = "proyectos"
            st.rerun()

        if st.button("📷 Inspecciones y Evaluaciones", use_container_width=True):
            st.session_state["modulo"] = "inspecciones"
            st.rerun()

    with col2:
        if st.button("👷 Control de Personal", use_container_width=True):
            st.session_state["modulo"] = "personal"
            st.rerun()

        if st.button("📄 Gestión Documental", use_container_width=True):
            st.session_state["modulo"] = "documentos"
            st.rerun()

    with col3:
        if st.button("📊 Reportes", use_container_width=True):
            st.session_state["modulo"] = "reportes"
            st.rerun()

        if st.button("⚙️ Configuración", use_container_width=True):
            st.session_state["modulo"] = "configuracion"
            st.rerun()


    # ---- ESTILO ----
    st.markdown(
        """
        <style>
            .stButton>button {
                border-radius: 15px;
                padding: 15px;
                font-size: 17px;
                font-weight: bold;
                border: 2px solid #3085C3;
                color: white;
                background: #3085C3;
                transition: 0.2s;
            }
            .stButton>button:hover {
                background: #2565A6;
                border-color: #2565A6;
                transform: scale(1.02);
            }
        </style>
        """,
        unsafe_allow_html=True
    )
