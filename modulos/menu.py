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

div.stButton {
    display: flex !important;
    justify-content: center !important;  /* Evita expandirse al 100% */
}

/* Estilo base de TODOS los botones */
div.stButton > button {
    width: 240px !important;   /* ← tamaño fijo horizontal */
    height: 90px !important;   /* ← tamaño fijo vertical */
    padding: 0 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    white-space: nowrap !important;   /* No permite que el texto salte de línea */
    overflow: hidden !important;      /* Evita que el texto desborde */
    text-overflow: ellipsis !important; /* Si el texto es largo → agrega "..." */

    font-size: 18px !important;
    font-weight: 600 !important;
    color: #4C3A60 !important;

    border-radius: 12px !important;
    border: none !important;

    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
}

/* Hover */
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
        modulos = [m for m in modulos_base if m[1] in ["proyectos", "inspecciones"]]
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
        col = cols[i % 3]
        with col:
            # Envolver el botón en el div con ID
            st.markdown(f"<div id='{css_id}'>", unsafe_allow_html=True)
            if st.button(texto, key=f"btn_{modulo}"):
                st.session_state.page = modulo
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    #               BOTÓN CERRAR SESIÓN
    # -----------------------------------------------------
    st.write("---")
    st.markdown("<div id='logout_btn'>", unsafe_allow_html=True)
    if st.button("🔒 Cerrar sesión", key="logout"):
        st.session_state.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
