import streamlit as st

def mostrar_menu():
    st.set_page_config(page_title="Panel Principal", layout="wide")

    # --- SIDEBAR ---
    with st.sidebar:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/9131/9131529.png",
            width=100
        )
        st.title("GAPC - Panel")
        if st.button("🔓 Cerrar sesión"):
            st.session_state["logged"] = False
            st.rerun()

    # --- TÍTULO ---
    st.markdown("""
        <h1 style="text-align:center; color:#3085C3;">
            🌟 Bienvenido al Sistema GAPC
        </h1>
        <p style="text-align:center; color:gray; font-size:18px;">
            Selecciona un módulo para continuar
        </p>
    """, unsafe_allow_html=True)

    # --- ESTILOS ---
    st.markdown("""
        <style>
        .round-btn > button {
            background-color: #3085C3 !important;
            color: white !important;
            padding: 20px !important;
            border-radius: 40px !important;
            font-size: 20px !important;
            font-weight: bold !important;
            width: 100% !important;
            height: 80px !important;
        }
        .round-btn > button:hover {
            background-color: #256a9e !important;
            transform: scale(1.03);
        }
        </style>
    """, unsafe_allow_html=True)

    # --- BOTONES EN 3 COLUMNAS ---
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container():
            if st.container().button("👤 Usuarios", key="usuarios", help="Administrar usuarios"):
                st.success("Abrir módulo de usuarios (aún no conectado)")

    with col2:
        with st.container():
            if st.container().button("📁 Expedientes", key="exp", help="Revisar expedientes"):
                st.success("Abrir módulo de expedientes (aún no conectado)")

    with col3:
        with st.container():
            if st.container().button("📊 Reportes", key="rep", help="Ver reportes"):
                st.success("Abrir módulo de reportes (aún no conectado)")
