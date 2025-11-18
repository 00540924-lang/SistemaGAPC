import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # -----------------------------------------------------
    #      🎨 CSS - Botones con animación + colores
    # -----------------------------------------------------

# Estilos para centrar y hacer grande el emoji
st.markdown("""
<style>
.emoji {
    font-size: 48px;
    text-align: center;
    margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)

# Crear columnas para organizar botones
cols = st.columns(3)

# Botón 1 - Gestión de Proyectos
with cols[0]:
    st.markdown("<div class='emoji'>📁</div>", unsafe_allow_html=True)
    if st.button("Gestión de Proyectos"):
        st.write("Presionaste Gestión de Proyectos")

# Botón 2 - Gestión de Usuarios
with cols[1]:
    st.markdown("<div class='emoji'>👥</div>", unsafe_allow_html=True)
    if st.button("Gestión de Usuarios"):
        st.write("Presionaste Gestión de Usuarios")

# Botón 3 - Grupos
with cols[2]:
    st.markdown("<div class='emoji'>📝</div>", unsafe_allow_html=True)
    if st.button("Grupos"):
        st.write("Presionaste Grupos")


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
        ("📝 Grupos", "grupos", "inspecciones_btn"),
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

