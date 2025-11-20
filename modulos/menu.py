import streamlit as st 

def mostrar_menu():
    rol = st.session_state.get("rol", None)
    usuario = st.session_state.get("usuario", "").lower()

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # -----------------------------------------------------
    #      🎨 CSS - Botones con animación + colores
    # -----------------------------------------------------
    st.markdown("""
<style>
div.stButton {
    display: flex !important;
    justify-content: center !important;
}

div.stButton > button {
    width: 240px !important;
    height: 90px !important;
    padding: 0 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;

    font-size: 18px !important;
    font-weight: 600 !important;
    color: #4C3A60 !important;

    border-radius: 12px !important;
    border: none !important;

    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
}

div.stButton > button:hover {
    transform: scale(1.07) !important;
    box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
}

/* Colores personalizados */
#proyectos_btn > button { background-color: #F4B400 !important; }
#usuarios_btn > button { background-color: #8E24AA !important; }
#grupos_btn > button { background-color: #E53935 !important; }
#documentos_btn > button { background-color: #1E88E5 !important; }
#reportes_btn > button { background-color: #43A047 !important; }
#configuracion_btn > button { background-color: #6D4C41 !important; }

/* Nuevo botón Asistencia */
#asistencia_btn > button { background-color: #FF7043 !important; }

# Nuevo botón GAPC
#gapc_btn > button { background-color: #29B6F6 !important; }

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
    #     NOMBRE DEL USUARIO (Y GRUPO O DESARROLLADOR)
    # -----------------------------------------------------
    st.markdown(
        f"<p style='text-align:center; font-size:18px; color:#4C3A60;'>Usuario: {st.session_state['usuario']}</p>",
        unsafe_allow_html=True
    )

    if usuario == "dark":
        st.markdown(
            "<p style='text-align:center; font-size:16px; color:#6D4C41;'>Desarrollador</p>",
            unsafe_allow_html=True
        )
    else:
        if st.session_state.get("nombre_grupo"):
            st.markdown(
                f"<p style='text-align:center; font-size:16px; color:#6D4C41;'>Grupo: {st.session_state['nombre_grupo']}</p>",
                unsafe_allow_html=True
            )

    # -----------------------------------------------------
    #                   MÓDULOS BASE
    # -----------------------------------------------------
    modulos_base = [
        ("📁 Credenciales", "credenciales", "proyectos_btn"),
        ("👥 Gestión de Miembros", "registrar_miembros", "usuarios_btn"),
        ("📝 Grupos", "grupos", "grupos_btn"),
        ("📜 Reglamento", "reglamento", "documentos_btn"),
        ("📊 Reportes", "reportes", "reportes_btn"),
        ("💸 Multas", "multas", "configuracion_btn"),
        ("📋 Asistencia", "asistencia", "asistencia_btn"),
        # GAPC (solo usuarios institucionales)
        ("🏛️ GAPC", "GAPC", "gapc_btn"),
    ]

    # -----------------------------------------------------
    #          FILTRO POR ROL
    # -----------------------------------------------------
    if usuario == "dark":
        modulos = modulos_base  # acceso total

    elif rol.lower() == "institucional":
        modulos = modulos_base  # acceso a todo + GAPC

    elif rol.lower() == "promotor":
        modulos = [m for m in modulos_base if m[1] in ["credenciales", "grupos"]]

    elif rol.lower() == "miembro":
        modulos = [m for m in modulos_base if m[1] in ["reglamento", "asistencia"]]

    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # -----------------------------------------------------
    #               GRID DE BOTONES
    # -----------------------------------------------------
    cols = st.columns(3)

    for i, (texto, modulo, css_id) in enumerate(modulos):
        with cols[i % 3]:
            cont = st.container()
            with cont:
                cont.markdown(f"<div id='{css_id}'>", unsafe_allow_html=True)
                if st.button(texto, key=f"btn_{modulo}"):
                    st.session_state.page = modulo
                    st.rerun()
                    return
            cont.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    #               BOTÓN CERRAR SESIÓN
    # -----------------------------------------------------
    st.write("---")
    logout_container = st.container()
    with logout_container:
        logout_container.markdown("<div id='logout_btn'>", unsafe_allow_html=True)
        if st.button("🔒 Cerrar sesión", key="logout"):
            st.session_state.clear()
            st.rerun()
