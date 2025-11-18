import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # -----------------------------------------------------
    #                    TÍTULO
    # -----------------------------------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # -----------------------------------------------------
    #      🎨 CSS - Botones con animación + colores + emoji grande
    # -----------------------------------------------------
    st.markdown("""
    <style>
    div.stButton > button {
        width: 240px !important;
        height: 100px !important;
        padding: 10px !important;

        display: flex !important;
        flex-direction: column !important;  /* Emoji arriba, texto abajo */
        align-items: center !important;
        justify-content: center !important;

        font-size: 18px !important;
        font-weight: 600 !important;
        color: #4C3A60 !important;

        border-radius: 12px !important;
        border: none !important;

        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
        white-space: normal !important; /* Permite texto multilinea */
    }
    div.stButton > button:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
    }
    /* Emoji grande estilo */
    div.stButton > button > span {
        font-size: 48px !important;
        line-height: 1 !important;
        margin-bottom: 5px !important;
    }

    /* Colores personalizados */
    #proyectos_btn > button { background-color: #F4B400 !important; }
    #usuarios_btn > button { background-color: #8E24AA !important; }
    #grupos_btn > button { background-color: #E53935 !important; }
    #documentos_btn > button { background-color: #1E88E5 !important; }
    #reportes_btn > button { background-color: #43A047 !important; }
    #configuracion_btn > button { background-color: #6D4C41 !important; }

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
    #                   MÓDULOS BASE
    # -----------------------------------------------------
    modulos_base = [
        ("📁\nGestión de Proyectos", "proyectos", "proyectos_btn"),
        ("👥\nGestión de Usuarios", "registrar_miembros", "usuarios_btn"),
        ("📝\nGrupos", "grupos", "grupos_btn"),
        ("📄\nGestión Documental", "documentos", "documentos_btn"),
        ("📊\nReportes", "reportes", "reportes_btn"),
        ("⚙️\nConfiguración", "configuracion", "configuracion_btn"),
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
    #               GRID DE BOTONES
    # -----------------------------------------------------
    cols = st.columns(3)

    for i, (texto, modulo, css_id) in enumerate(modulos):
        with cols[i % 3]:
            # El id se asigna al div contenedor para que el CSS funcione
            st.markdown(f"<div id='{css_id}'>", unsafe_allow_html=True)
            clicked = st.button(texto, key=f"btn_{modulo}")
            st.markdown("</div>", unsafe_allow_html=True)

            if clicked:
                st.session_state.page = modulo
                st.experimental_rerun()

    # -----------------------------------------------------
    #               BOTÓN CERRAR SESIÓN
    # -----------------------------------------------------
    st.write("---")

    logout_container = st.container()
    with logout_container:
        st.markdown("<div id='logout_btn'>", unsafe_allow_html=True)
        logout = st.button("🔒 Cerrar sesión", key="logout")
        st.markdown("</div>", unsafe_allow_html=True)

        if logout:
            st.session_state.clear()
            st.experimental_rerun()


# Ejemplo para probar la función directamente:
if __name__ == "__main__":
    if "rol" not in st.session_state:
        st.session_state["rol"] = "institucional"  # Puedes cambiar para testear otros roles
    mostrar_menu()
