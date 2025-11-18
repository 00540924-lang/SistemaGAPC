import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # -----------------------------------------------------
    #                    CSS
    # -----------------------------------------------------
    st.markdown("""
    <style>
    div.stButton > button {
        width: 240px !important;
        height: 90px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: none !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        color: white !important;
    }
    div.stButton > button:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0,0,0,0.3) !important;
    }
    /* Colores por orden (importante: coincidir con el orden de los botones) */
    div.stButton > button:nth-of-type(1) { background-color: #F4B400; color:#4C3A60; }
    div.stButton > button:nth-of-type(2) { background-color: #8E24AA; }
    div.stButton > button:nth-of-type(3) { background-color: #E53935; }
    div.stButton > button:nth-of-type(4) { background-color: #1E88E5; }
    div.stButton > button:nth-of-type(5) { background-color: #43A047; }
    div.stButton > button:nth-of-type(6) { background-color: #6D4C41; }

    /* Logout */
    #logout_btn > button {
        width: 200px !important;
        height: 60px !important;
        background-color: #424242 !important;
        color: white !important;
        border-radius: 10px !important;
        transition: transform 0.2s ease !important;
    }
    #logout_btn > button:hover {
        transform: scale(1.05) !important;
        background-color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------
    #                    TÍTULO
    # -----------------------------------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # -----------------------------------------------------
    #                   MÓDULOS BASE
    # -----------------------------------------------------
    modulos_base = [
        ("📁 Gestión de Proyectos", "proyectos"),
        ("👥 Gestión de Usuarios", "registrar_miembros"),
        ("📝 Grupos", "grupos"),
        ("📄 Gestión Documental", "documentos"),
        ("📊 Reportes", "reportes"),
        ("⚙️ Configuración", "configuracion"),
    ]

    # -----------------------------------------------------
    #               FILTRO POR ROL
    # -----------------------------------------------------
    if rol == "institucional":
        modulos = modulos_base
    elif rol == "promotor":
        modulos = [m for m in modulos_base if m[1] in ["proyectos", "grupos"]]
    elif rol == "miembro":
        modulos = [m for m in modulos_base if m[1] == "documentos"]
    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # -----------------------------------------------------
    #               BOTONES STREAMLIT
    # -----------------------------------------------------
    cols = st.columns(3)
    for i, (texto, modulo) in enumerate(modulos):
        with cols[i % 3]:
            if st.button(texto, key=f"btn_{modulo}"):
                st.session_state.page = modulo
                st.rerun()

    # -----------------------------------------------------
    #               BOTÓN CERRAR SESIÓN
    # -----------------------------------------------------
    st.write("---")
    with st.container():
        if st.button("🔒 Cerrar sesión", key="logout"):
            st.session_state.clear()
            st.rerun()

