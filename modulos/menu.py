import streamlit as st

def mostrar_menu():
    # obtener rol
    rol = st.session_state.get("rol", None)

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
        color: #FAFAFA !important;
        border-radius: 12px !important;
        border: none !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
    }

    div.stButton > button:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
    }

    /* Selectores que funcionan con la estructura real de Streamlit */
    #proyectos_btn   .stButton > button { background-color: #F4B400 !important; }
    #usuarios_btn    .stButton > button { background-color: #8E24AA !important; }
    #grupos_btn      .stButton > button { background-color: #E53935 !important; }
    #documentos_btn  .stButton > button { background-color: #1E88E5 !important; }
    #reportes_btn    .stButton > button { background-color: #43A047 !important; }
    #configuracion_btn .stButton > button { background-color: #6D4C41 !important; }

    /* Logout */
    #logout_btn .stButton > button {
        width: 200px !important;
        height: 60px !important;
        background-color: #424242 !important;
        color: white !important;
        border-radius: 10px !important;
    }
    #logout_btn .stButton > button:hover {
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
        ("📝 Grupos", "grupos", "grupos_btn"),               # <-- usar grupos_btn aquí
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
        # si no existe "inspecciones" en modulos_base, ajusta a los nombres válidos
        modulos = [m for m in modulos_base if m[1] in ["proyectos", "grupos"]]

    elif rol == "miembro":
        modulos = [m for m in modulos_base if m[1] == "documentos"]

    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # -----------------------------------------------------
    #               GRID DE BOTONES (CORRECTAMENTE ENLAZADOS CON IDs)
    # -----------------------------------------------------
    cols = st.columns(3)

    for i, (texto, modulo, css_id) in enumerate(modulos):
        with cols[i % 3]:
            # Abrimos el contenedor con el ID (el truco: colocarlo justo antes del botón)
            st.markdown(f"<div id='{css_id}'>", unsafe_allow_html=True)

            # El botón quedará renderizado por Streamlit; el selector CSS se basa en la estructura generada
            pressed = st.button(texto, key=f"btn_{modulo}")

            # Cerramos el div
            st.markdown("</div>", unsafe_allow_html=True)

            if pressed:
                st.session_state.page = modulo
                st.rerun()

    # -----------------------------------------------------
    #               BOTÓN CERRAR SESIÓN (envuelto igual que los demás)
    # -----------------------------------------------------
    st.write("---")

    # Usar la misma técnica para el logout para que el selector CSS lo encuentre
    st.markdown("<div id='logout_btn'>", unsafe_allow_html=True)
    logout = st.button("🔒 Cerrar sesión", key="logout")
    st.markdown("</div>", unsafe_allow_html=True)

    if logout:
        # limpia la sesión y redirige
        st.session_state.clear()
        st.rerun()

