import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

# -----------------------------------------------------
#      🎨 CSS - Botones centrados con animación
# -----------------------------------------------------
st.markdown("""
<style>

 /* CENTRAR TODOS LOS BOTONES */
 .center-buttons button {
     margin-left: auto !important;
     margin-right: auto !important;
     display: block !important;
 }

 /* BOTONES: estilo base */
 div.stButton > button {
     color: #4C3A60 !important;
     border-radius: 12px !important;
     padding: 20px !important;
     font-size: 18px !important;
     font-weight: 600 !important;
     width: 350px !important;
     height: 100px !important;
     border: none !important;
     transition: transform 0.25s ease, box-shadow 0.25s ease !important;
     box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
 }

 /* ANIMACIÓN */
 div.stButton > button:hover {
     transform: scale(1.07) !important;
     box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
 }

 /* COLORES */
 #proyectos_btn > button { background-color: #F4B400 !important; }
 #usuarios_btn > button { background-color: #8E24AA !important; }
 #inspecciones_btn > button { background-color: #E53935 !important; }
 #documentos_btn > button { background-color: #1E88E5 !important; }
 #reportes_btn > button { background-color: #43A047 !important; }
 #configuracion_btn > button { background-color: #6D4C41 !important; }

 /* CERRAR SESIÓN */
 #logout_btn > button {
     background-color: #424242 !important;
     color: white !important;
     width: 200px !important;
     border-radius: 10px !important;
 }
 #logout_btn > button:hover {
     transform: scale(1.05) !important;
     background-color: #000000 !important;
 }

</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------
#      🚀 BOTONES — SIN DIV CONTENEDOR
# -----------------------------------------------------

st.markdown('<div class="center-buttons">', unsafe_allow_html=True)

st.button("Proyectos", key="proyectos_btn")
st.button("Usuarios", key="usuarios_btn")
st.button("Inspecciones", key="inspecciones_btn")
st.button("Documentos", key="documentos_btn")
st.button("Reportes", key="reportes_btn")
st.button("Configuración", key="configuracion_btn")
st.button("Cerrar sesión", key="logout_btn")

st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------
    #                   MÓDULOS BASE
    # -----------------------------------------------------
    modulos_base = [
        ("📁 Gestión de Proyectos", "proyectos", "proyectos_btn"),
        ("👥 Gestión de Usuarios", "registrar_miembros", "usuarios_btn"),
        ("📝 Inspecciones y Evaluaciones", "inspecciones", "inspecciones_btn"),
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
            btn = st.container()
            with btn:
                b = st.button(texto, key=f"btn_{modulo}")
                # Aplicar ID de CSS al contenedor
                btn.markdown(f"<div id='{css_id}'></div>", unsafe_allow_html=True)

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
