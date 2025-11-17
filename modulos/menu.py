    # -------- BOTÓN CERRAR SESIÓN --------
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # CSS para el botón con el gradiente igual a la tarjeta
    st.markdown(
        """
        <style>
        .logout-btn-custom {
            background: linear-gradient(135deg, #B7A2C8, #F7C9A4);
            padding: 12px 26px;
            color: white !important;
            font-weight: bold;
            font-size: 20px;
            border-radius: 14px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            cursor: pointer;
            border: none;
            box-shadow: 0px 6px 14px rgba(0,0,0,0.18);
            transition: 0.20s ease-in-out;
        }
        .logout-btn-custom:hover {
            transform: translateY(-4px) scale(1.03);
            box-shadow: 0px 12px 22px rgba(0,0,0,0.25);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Botón verdadero centrado
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        if st.button("🔒 Cerrar sesión", key="logout_button"):
            st.session_state.clear()
            st.rerun()

