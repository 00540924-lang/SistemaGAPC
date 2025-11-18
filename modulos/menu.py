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
button.custom-btn {
    width: 200px;
    height: 150px;
    font-size: 18px;
    font-weight: 600;
    border-radius: 12px;
    border: none;
    color: white;
    cursor: pointer;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    margin: 10px 0;
}

/* Hover general */
button.custom-btn:hover {
    transform: scale(1.07);
    box-shadow: 0 10px 22px rgba(0,0,0,0.3);
}

/* Colores específicos */
button#proyectos { background-color: #F4B400; }
button#usuarios { background-color: #8E24AA; }
button#grupos { background-color: #E53935; }
button#documentos { background-color: #1E88E5; }
button#reportes { background-color: #43A047; }
button#configuracion { background-color: #6D4C41; }
button#logout {
    background-color: #424242;
    height: 60px;
    border-radius: 10px;
}
button#logout:hover { background-color: black; transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

# --------------------------
# Función para crear botones HTML
# --------------------------
def html_button(label, btn_id):
    return st.markdown(f'<button class="custom-btn" id="{btn_id}">{label}</button>', unsafe_allow_html=True)

# --------------------------
# Botones
# --------------------------
html_button("Proyectos", "proyectos")
html_button("Usuarios", "usuarios")
html_button("Grupos", "grupos")
html_button("Documentos", "documentos")
html_button("Reportes", "reportes")
html_button("Configuración", "configuracion")
html_button("Logout", "logout")

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
