import streamlit as st

def mostrar_menu():

    # ---------------------------------------
    # LEER ROL DEL USUARIO DESDE EL LOGIN
    # ---------------------------------------
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        st.stop()

    # ---------------------------------------
    # CONFIGURAR MÓDULOS SEGÚN ROL
    # ---------------------------------------
    if rol == "institucional":
        modulos = [
            ("📁", "Gestión de Proyectos", "proyectos"),
            ("👥", "Gestión de Usuarios", "usuarios"),
            ("🧾", "Inspecciones y Evaluaciones", "inspecciones"),
            ("📄", "Gestión Documental", "documentos"),
            ("📊", "Reportes", "reportes"),
            ("⚙️", "Configuración", "configuracion"),
        ]

    elif rol == "promotor":
        modulos = [
            ("📁", "Gestión de Proyectos", "proyectos"),
            ("🧾", "Inspecciones y Evaluaciones", "inspecciones"),
        ]

    elif rol == "miembro":
        modulos = [
            ("📄", "Gestión Documental", "documentos"),
        ]

    else:
        st.error("❌ Rol no reconocido.")
        st.stop()

    # ---------------------------------------
    # TÍTULO
    # ---------------------------------------
    st.markdown("""
        <h1 style='text-align:center; color:#4C3A60; font-size: 36px; margin-bottom:4px'>
            Menú Principal – GAPC
        </h1>
        """, unsafe_allow_html=True)

    # Tarjeta encabezado
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #B7A2C8, #F7C9A4);
            padding: 3px;
            border-radius: 12px;
            color: #4C3A60;
            font-size: 18px;
            text-align: center;
            width: 80%;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
            margin: auto;
        ">
            <b>Seleccione un módulo para continuar</b>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------
    # CSS — TARJETAS NEUMÓRFICAS PREMIUM
    # ---------------------------------------
    st.markdown("""
<style>

button[kind="secondary"] {
    width: 170px !important;
    height: 170px !important;

    background: #e3e3e3 !important;

    border-radius: 25px !important;
    border: none !important;

    font-size: 20px !important;
    font-weight: 700 !important;
    color: #4C3A60 !important;

    padding: 20px !important;

    box-shadow:
        8px 8px 16px rgba(0,0,0,0.18),
        -8px -8px 16px rgba(255,255,255,0.8) !important;

    transition: all 0.22s ease-in-out !important;
}

button[kind="secondary"]:hover {
    transform: translateY(-8px) scale(1.04) !important;

    box-shadow:
        12px 12px 22px rgba(0,0,0,0.22),
        -10px -10px 20px rgba(255,255,255,0.9) !important;
}

button[kind="secondary"]:active {
    transform: scale(0.97) !important;

    box-shadow:
        inset 5px 5px 12px rgba(0,0,0,0.25),
        inset -5px -5px 12px rgba(255,255,255,0.7) !important;
}

</style>
""", unsafe_allow_html=True)

    # ---------------------------------------
    # GRID DE BOTONES
    # ---------------------------------------
    st.write("")
    cols = st.columns(3)

    for i, (icono, texto, modulo) in enumerate(modulos):
        with cols[i % 3]:
            if st.button(f"{icono}\n{texto}", key=f"btn_{modulo}"):
                st.session_state["modulo"] = modulo
                st.rerun()

    # ---------------------------------------
    # BOTÓN CERRAR SESIÓN
    # ---------------------------------------
    st.write("")
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("🔒 Cerrar sesión", key="cerrar_sesion_btn"):
            st.session_state.clear()
            st.rerun()
