import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # -----------------------------------------------------
    # CSS para botones con animación y colores
    # -----------------------------------------------------
    st.markdown("""
    <style>
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        margin: 10px 0;
    }

    div.stButton > button {
        width: 240px;
        height: 90px;
        padding: 0;

        display: flex;
        align-items: center;
        justify-content: center;

        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;

        font-size: 18px;
        font-weight: 600;
        color: #4C3A60;

        border-radius: 12px;
        border: none;

        transition: transform 0.25s ease, box-shadow 0.25s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18);
    }

    div.stButton > button:hover {
        transform: scale(1.07);
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30);
    }

    .proyectos_btn > button { background-color: #F4B400; }
    .usuarios_btn > button { background-color: #8E24AA; color: white; }
    .grupos_btn > button { background-color: #E53935; color: white; }
    .documentos_btn > button { background-color: #1E88E5; color: white; }
    .reportes_btn > button { background-color: #43A047; color: white; }
    .configuracion_btn > button { background-color: #6D4C41; color: white; }

    .logout_btn > button {
        width: 200px;
        height: 60px;
        background-color: #424242;
        color: white;
        border-radius: 10px;
        transition: transform 0.2s ease;
    }
    .logout_btn > button:hover {
        transform: scale(1.05);
        background-color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # Título
    # -----------------------------------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # Módulos base
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
    # Filtro por rol
    # -----------------------------------------------------
    if rol == "institucional":
        modulos = modulos_base
    elif rol == "promotor":
        modulos = [m for m in modulos_base if m[1] in ["proyectos", "inspecciones"]]
    elif rol == "miembro":
        modulos = [m for m in modulos_base if m[1] == "documentos"]
    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # -----------------------------------------------------
    # Grid de botones (3 columnas)
    # -----------------------------------------------------
    cols = st.columns(3)
    for i, (texto, modulo, css_class) in enumerate(modulos):
        col = cols[i % 3]
        with col:
            st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
            if st.button(texto, key=f"btn_{modulo}"):
                st.session_state.page = modulo
            st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # Botón cerrar sesión
    # -----------------------------------------------------
    st.write("---")
    st.markdown("<div class='logout_btn'>", unsafe_allow_html=True)
    if st.button("🔒 Cerrar sesión", key="logout"):
        st.session_state.clear()
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

