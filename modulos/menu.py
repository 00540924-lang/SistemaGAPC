import streamlit as st

def mostrar_menu():

    st.markdown(
        """
        <h1 style='text-align:center; color:#4C3A60; font-size: 36px; margin-bottom:4px'>
            Menú Principal – GAPC
        </h1>
        """,
        unsafe_allow_html=True,
    )

    # -------- TARJETA VISUAL -----------
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #B7A2C8, #F7C9A4);
            padding: 3px;
            border-radius: 12px;
            color: #ffffff;
            font-size: 18px;
            text-align: center;
            width: 80%;
            margin: auto;
        ">
            <b>Seleccione un módulo para continuar</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------- CSS --------
    st.markdown(
        """
        <style>
        .cards-row {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        .card {
            width: 160px;
            height: 150px;
            border-radius: 16px;
            padding: 18px;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-weight: 700;
            font-size: 40px;
            cursor: pointer;
            transition: 0.2s ease;
        }
        .card:hover {
            transform: translateY(-8px) scale(1.04);
            box-shadow: 0 12px 30px rgba(0,0,0,0.20);
        }
        .g1 { background: linear-gradient(135deg, #3085C3, #5BB3E6); }
        .g2 { background: linear-gradient(135deg, #6A4BAF, #C08BE6); }
        .g3 { background: linear-gradient(135deg, #FF9A56, #FEEAA1); }
        .g4 { background: linear-gradient(135deg, #1ABC9C, #7BE3C6); }
        .g5 { background: linear-gradient(135deg, #FF6B6B, #FFABAB); }
        .g6 { background: linear-gradient(135deg, #9A86AE, #D6CDE2); }

        .card-sub {
            font-size: 15px;
            font-weight: 600;
            opacity: 0.95;
            text-align: center;
        }

        .logout-btn {
            background: linear-gradient(135deg, #FF6B6B, #FFABAB);
            color: white;
            padding: 10px 25px;
            width: 220px;
            text-align: center;
            font-weight: 700;
            font-size: 17px;
            border-radius: 10px;
            border: none;
            margin-top: 25px;
        }
        .logout-btn:hover {
            transform: scale(1.05);
            box-shadow: 0px 4px 14px rgba(0,0,0,0.2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    # -------- TARJETAS --------
    card_map = {
        "proyectos": ("📁", "Gestión de Proyectos", "g1"),
        "personal": ("👥", "Control de Personal", "g2"),
        "inspecciones": ("🧾", "Inspecciones", "g3"),
        "documentos": ("📄", "Gestión Documental", "g4"),
        "reportes": ("📊", "Reportes", "g5"),
        "configuracion": ("⚙️", "Configuración", "g6"),
    }

    cols = st.columns(3, gap="large")

    idx = 0
    for pagina, data in card_map.items():
        icono, titulo, clase = data
        with cols[idx % 3]:
            if st.button(f"{icono}\n{titulo}", key=f"btn_{pagina}"):
                st.session_state["pagina_actual"] = pagina
                st.rerun()

        idx += 1

    st.write("")
    st.write("")

    # -------- CERRAR SESIÓN ----------
    if st.button("🔒 Cerrar sesión", key="logout"):
        st.session_state.clear()
        st.rerun()
