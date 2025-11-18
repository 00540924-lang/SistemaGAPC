import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # -----------------------------------------------------
    #      🎨 CSS - Botones con animación + colores
    # -----------------------------------------------------
    
# --------------------------
# CSS para botones
# --------------------------
st.markdown("""
<style>
/* Centrar botones */
div[data-testid="stButton"] {
    display: flex;
    justify-content: center;
    margin: 10px 0;
}

/* Estilo general */
div[data-testid="stButton"] > button {
    width: 200px;
    height: 150px;
    font-size: 18px;
    font-weight: 600;
    border-radius: 12px;
    border: none;
    color: white;
    cursor: pointer;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    box-shadow: 0 4px 10px rgba(0,0,0,0.18);
}

/* Hover general */
div[data-testid="stButton"] > button:hover {
    transform: scale(1.07);
    box-shadow: 0 10px 22px rgba(0,0,0,0.3);
}

/* Colores de botones específicos */
div[data-testid="stButton"] > button:nth-of-type(1) { background-color: #F4B400; }
div[data-testid="stButton"] > button:nth-of-type(2) { background-color: #8E24AA; }
div[data-testid="stButton"] > button:nth-of-type(3) { background-color: #E53935; }
div[data-testid="stButton"] > button:nth-of-type(4) { background-color: #1E88E5; }
div[data-testid="stButton"] > button:nth-of-type(5) { background-color: #43A047; }
div[data-testid="stButton"] > button:nth-of-type(6) { background-color: #6D4C41; }

/* Botón logout más pequeño */
div[data-testid="stButton"] > button:nth-of-type(7) {
    width: 200px;
    height: 60px;
    background-color: #424242;
    border-radius: 10px;
}
div[data-testid="stButton"] > button:nth-of-type(7):hover {
    background-color: black;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Botones en Python
# --------------------------
if st.button("Proyectos"):
    st.write("Botón Proyectos clickeado")

if st.button("Usuarios"):
    st.write("Botón Usuarios clickeado")

if st.button("Grupos"):
    st.write("Botón Grupos clickeado")

if st.button("Documentos"):
    st.write("Botón Documentos clickeado")

if st.button("Reportes"):
    st.write("Botón Reportes clickeado")

if st.button("Configuración"):
    st.write("Botón Configuración clickeado")

if st.button("Logout"):
    st.write("Has cerrado sesión")
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
