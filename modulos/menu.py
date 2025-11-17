import streamlit as st

def mostrar_menu():

    st.markdown(
        """
        <h2 style="text-align: center; margin-bottom: 20px;">
            Panel Principal – Sistema GAPC
        </h2>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------
    #   ESTILOS PARA BOTONES TARJETA
    # ------------------------------
    st.markdown(
        """
        <style>

        .card-container {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 25px;
            margin-top: 30px;
        }

        .card {
            width: 260px;
            height: 140px;
            background: linear-gradient(135deg, #3085C3, #FEEAA1);
            border-radius: 18px;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-size: 23px;
            font-weight: bold;
            text-align: center;
            cursor: pointer;
            transition: 0.3s ease-in-out;
            box-shadow: 0px 6px 12px rgba(0,0,0,0.15);
        }

        .card:hover {
            transform: scale(1.07);
            box-shadow: 0px 10px 20px rgba(0,0,0,0.25);
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------
    #     TARJETAS COMO BOTONES (ACCIONES REALES)
    # -----------------------------------------------
    st.markdown("<div class='card-container'>", unsafe_allow_html=True)

    # Usamos botones invisibles encima de tarjetas HTML
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    # ---- BOTONES ----
    if col1.button("📊 Dashboard", key="btn_dashboard"):
        st.session_state["modulo_actual"] = "dashboard"

    if col2.button("👥 Grupos", key="btn_grupos"):
        st.session_state["modulo_actual"] = "grupos"

    if col3.button("🧾 Reuniones", key="btn_reuniones"):
        st.session_state["modulo_actual"] = "reuniones"

    if col4.button("💰 Caja", key="btn_caja"):
        st.session_state["modulo_actual"] = "caja"

    if col5.button("📄 Reportes", key="btn_reportes"):
        st.session_state["modulo_actual"] = "reportes"

    if col6.button("⚙️ Configuración", key="btn_config"):
        st.session_state["modulo_actual"] = "configuracion"

    # ---- Tarjetas Visuales (solo estética) ----
    st.markdown(
        """
        <div class='card-container'>
            <div class='card'>📊 <br> Dashboard</div>
            <div class='card'>👥 <br> Grupos</div>
            <div class='card'>🧾 <br> Reuniones</div>
            <div class='card'>💰 <br> Caja</div>
            <div class='card'>📄 <br> Reportes</div>
            <div class='card'>⚙️ <br> Configuración</div>
        </div>
        """,
        unsafe_allow_html=True
    )



