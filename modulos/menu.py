import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # ----------------------------
    # CSS PARA BOTONES ANIMADOS
    # ----------------------------
    st.markdown("""
    <style>
    .menu-btn > button {
        background-color: #ffffff !important;
        color: #333 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        border: 1px solid #e0e0e0 !important;
        width: 100% !important;
        height: 110px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
        transition: all 0.25s ease-in-out !important;
    }
    .menu-btn > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15) !important;
        border-color: #bbbbbb !important;
    }
    .logout-btn > button {
        background-color: #d9534f !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        width: 200px !important;
        transition: all .2s ease !important;
    }
    .logout-btn > button:hover {
        background-color: #c9302c !important;
        transform: scale(1.03) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ----------------------------
    # TÍTULO
    # ----------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # ----------------------------
    # LISTA BASE DE MÓDULOS
    # ----------------------------
    modulos_base = [
        ("📁 Gestión de Proyectos", "proyectos"),
        ("👥 Gestión de Usuarios", "registrar_miembros"),
        ("📝 Inspecciones y Evaluaciones", "inspecciones"),
        ("📄 Gestión Documental", "documentos"),
        ("📊 Reportes", "reportes"),
        ("⚙️ Configuración", "configuracion"),
    ]

    # ----------------------------
    # LÓGICA DE ROLES
    # ----------------------------
    if rol == "institucional":
        modulos = modulos_base

    elif rol == "promotor":
        modulos = [
            m for m in modulos_base
            if m[1] in ["proyectos", "inspecciones"]
        ]

    elif rol == "miembro":
        modulos = [
            m for m in modulos_base
            if m[1] == "documentos"
        ]

    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # ----------------------------
    # GRID DE BOTONES
    # ----------------------------
    cols = st.columns(3)

    for i, (texto, modulo) in enumerate(modulos):
        with cols[i % 3]:
            with st.container():
                btn = st.button(
                    texto,
                    key=f"btn_{modulo}",
                    use_container_width=True,
                    type="secondary"
                )
                # Aplicamos clase CSS al botón
                st.markdown("<div class='menu-btn'></div>", unsafe_allow_html=True)

                if btn:
                    st.session_state.page = modulo
                    st.rerun()

    # ----------------------------
    # BOTÓN DE CERRAR SESIÓN
    # ----------------------------
    st.write("---")
    with st.container():
        logout = st.button("🔒 Cerrar sesión", key="logout")
        st.markdown("<div class='logout-btn'></div>", unsafe_allow_html=True)

        if logout:
            st.session_state.clear()
            st.rerun()
