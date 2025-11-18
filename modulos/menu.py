import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)
    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # CSS para personalizar botones específicos según su key
    st.markdown("""
    <style>
    /* Botón proyectos */
    button[kind="primary"][data-testid="stButton"][aria-label="btn_proyectos"] {
        background-color: #F4B400 !important;
        color: #4C3A60 !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
    }
    /* Botón usuarios */
    button[kind="primary"][data-testid="stButton"][aria-label="btn_registrar_miembros"] {
        background-color: #8E24AA !important;
        color: white !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
    }
    /* Botón grupos */
    button[kind="primary"][data-testid="stButton"][aria-label="btn_grupos"] {
        background-color: #E53935 !important;
        color: white !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
    }
    /* Botón documentos */
    button[kind="primary"][data-testid="stButton"][aria-label="btn_documentos"] {
        background-color: #1E88E5 !important;
        color: white !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
    }
    /* Botón reportes */
    button[kind="primary"][data-testid="stButton"][aria-label="btn_reportes"] {
        background-color: #43A047 !important;
        color: white !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
    }
    /* Botón configuración */
    button[kind="primary"][data-testid="stButton"][aria-label="btn_configuracion"] {
        background-color: #6D4C41 !important;
        color: white !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
    }
    /* Botón logout */
    button[kind="primary"][data-testid="stButton"][aria-label="logout_btn"] {
        background-color: #424242 !important;
        color: white !important;
        width: 200px !important;
        height: 60px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        border-radius: 10px !important;
    }
    button[kind="primary"][data-testid="stButton"][aria-label="logout_btn"]:hover {
        background-color: #000000 !important;
        transform: scale(1.05) !important;
        transition: all 0.2s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    modulos_base = [
        ("📁 Gestión de Proyectos", "proyectos"),
        ("👥 Gestión de Usuarios", "registrar_miembros"),
        ("📝 Grupos", "grupos"),
        ("📄 Gestión Documental", "documentos"),
        ("📊 Reportes", "reportes"),
        ("⚙️ Configuración", "configuracion"),
    ]

    # Filtrado rol
    if rol == "institucional":
        modulos = modulos_base
    elif rol == "promotor":
        modulos = [m for m in modulos_base if m[1] in ["proyectos", "grupos"]]
    elif rol == "miembro":
        modulos = [m for m in modulos_base if m[1] == "documentos"]
    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    cols = st.columns(3)
    for i, (texto, modulo) in enumerate(modulos):
        with cols[i % 3]:
            if st.button(texto, key=f"btn_{modulo}", help=texto):
                st.session_state.page = modulo
                st.experimental_rerun()

    st.markdown("---")

    if st.button("🔒 Cerrar sesión", key="logout_btn"):
        st.session_state.clear()
        st.experimental_rerun()
