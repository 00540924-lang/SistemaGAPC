import streamlit as st

def mostrar_menu():

    st.markdown(
        """
        <h2 style="text-align: center; margin-bottom: 10px;">
            Panel principal – GAPC
        </h2>
        """,
        unsafe_allow_html=True
    )

    # ---- Estilos CSS de botones modernos ----
    st.markdown(
        """
        <style>

        .card-btn {
            background: linear-gradient(135deg, #3085C3, #FEEAA1);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            font-weight: bold;
            color: white;
            font-size: 18px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
            transition: 0.3s;
            cursor: pointer;
        }

        .card-btn:hover {
            transform: scale(1.05);
            box-shadow: 0px 6px 15px rgba(0,0,0,0.25);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---- GRID de botones ----
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Dashboard", key="dash"):
            st.session_state["modulo_actual"] = "dashboard"

    with col2:
        if st.button("👤 Usuarios", key="users"):
            st.session_state["modulo_actual"] = "usuarios"

    with col3:
        if st.button("📁 Proyectos", key="proyectos"):
            st.session_state["modulo_actual"] = "proyectos"

    st.write("")

    col4, col5, col6 = st.columns(3)

    with col4:
        if st.button("📦 Inventario", key="invent"):
            st.session_state["modulo_actual"] = "inventario"

    with col5:
        if st.button("📄 Reportes", key="reportes"):
            st.session_state["modulo_actual"] = "reportes"

    with col6:
        if st.button("⚙️ Configuración", key="config"):
            st.session_state["modulo_actual"] = "configuracion"


