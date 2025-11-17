import streamlit as st

# -------------------------------------------------
# VISTA DESPUÉS DE INICIAR SESIÓN
# -------------------------------------------------
def menu_principal():

    st.markdown(
        """
        <h2 style='text-align: center; color:#4C3A60;'>
            Menú Principal – Sistema GAPC
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.write("### 👋 Bienvenido, {}".format(st.session_state["usuario"]))

    st.write("")

    # ---- TARJETAS DE MÓDULOS ----
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state["modulo"] = "dashboard"

        if st.button("👥 Usuarios", use_container_width=True):
            st.session_state["modulo"] = "usuarios"

    with col2:
        if st.button("💰 Préstamos", use_container_width=True):
            st.session_state["modulo"] = "prestamos"

        if st.button("📂 Ahorros", use_container_width=True):
            st.session_state["modulo"] = "ahorros"

    with col3:
        if st.button("📑 Reportes", use_container_width=True):
            st.session_state["modulo"] = "reportes"

        if st.button("⚙️ Configuración", use_container_width=True):
            st.session_state["modulo"] = "configuracion"

    st.write("---")

    # ---- CERRAR SESIÓN ----
    if st.button("🚪 Cerrar sesión", type="secondary"):
        st.session_state["sesion_iniciada"] = False
        st.session_state["usuario"] = ""
        st.session_state["modulo"] = None
        st.rerun()
