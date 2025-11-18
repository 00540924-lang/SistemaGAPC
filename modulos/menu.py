import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # -----------------------------------------------------
    #      🎨 CSS - Botones con animación + colores
    # -----------------------------------------------------
    st.markdown("""
    <style>

    div.stButton > button {
        color: #4C3A60 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        width: 100% !important;
        height: 110px !important;
        border: none !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
    }

    div.stButton > button:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
    }

    #proyectos_btn > button { background-color: #F4B400 !important; }
    #usuarios_btn > button { background-color: #8E24AA !important; }
    #grupos_btn > button { background-color: #E53935 !important; }
    #documentos_btn > button { background-color: #1E88E5 !important; }
    #reportes_btn > button { background-color: #43A047 !important; }
    #configuracion_btn > button { background-color: #6D4C41 !important; }

    #logout_btn > button {
        background-color: #424242 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 12px 22px !important;
        font-size: 16px !important;
        width: 200px !important;
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
        ("📁 Gestión de Proyectos", "proyectos", "proyectos_btn"),
        ("👥 Gestión de Usuarios", "registrar_miembros", "usuarios_btn"),
        ("📝 Grupos", "grupos", "grupos_btn"),
        ("📄 Gestión Documental", "documentos", "documentos_btn"),
        ("📊 Reportes", "reportes", "reportes_btn"),
        ("⚙️ Configuración", "configuracion", "configuracion_btn"),
    ]

    # -----------------------------------------------------
    #               FILTRO POR ROL
    # -----------------------------------------------------
    if rol == "institucional":
        modulos = modulos_base

    elif rol == "promotor":
        modulos = [
            m for m in modulos_base if m[1] in ["proyectos", "inspecciones"]
        ]

    elif rol == "miembro":
        modulos = [
            m for m in modulos_base if m[1] == "documentos"
        ]

    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # -----------------------------------------------------
    #               GRID DE BOTONES
    # -----------------------------------------------------
    cols = st.columns(3)

    for i, (texto, modulo, css_id) in enumerate(modulos):
        with cols[i % 3]:
            container = st.container()
            with container:
                b = st.button(texto, key=f"btn_{modulo}")
                container.markdown(f"<div id='{css_id}'></div>", unsafe_allow_html=True)

                if b:
                    st.session_state.page = modulo
                    st.rerun()

    # -----------------------------------------------------
    #               BOTÓN CERRAR SESIÓN
    # -----------------------------------------------------
    st.write("---")

    logout_container = st.container()
    with logout_container:
        logout = st.button("🔒 Cerrar sesión", key="logout")
        logout_container.markdown("<div id='logout_btn'></div>", unsafe_allow_html=True)

        if logout:
            st.session_state.clear()
            st.rerun()
