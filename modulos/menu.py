import streamlit as st

def mostrar_menu():

    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # ======================================================
    # ⚡️ EVITAR PARPADEO (REDIRECCIÓN ANTES DEL MENÚ)
    # ======================================================
    if "go_to_page" in st.session_state:
        page = st.session_state.pop("go_to_page")
        st.session_state.page = page
        st.rerun()

    # ======================================================
    # 🎨 CSS
    # ======================================================
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

/* Colores */
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
}
#logout_btn > button:hover {
    transform: scale(1.05) !important;
    background-color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

    # ======================================================
    # 🏷️ TÍTULO
    # ======================================================
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # ======================================================
    # 📌 MÓDULOS DEFINIDOS
    # ======================================================
    modulos_base = [
        ("📁 Credenciales", "credenciales", "proyectos_btn"),
        ("👥 Gestión de Miembros", "registrar_miembros", "usuarios_btn"),
        ("📝 Grupos", "grupos", "grupos_btn"),
        ("📜 Reglamento", "reglamento", "documentos_btn"),
        ("📊 Reportes", "reportes", "reportes_btn"),
        ("⚙️ Configuración", "configuracion", "configuracion_btn"),
    ]

    # ======================================================
    # 🎚️ FILTRO POR ROL
    # ======================================================
    if rol == "institucional":
        modulos = modulos_base
    elif rol == "promotor":
        modulos = [m for m in modulos_base if m[1] in ["proyectos", "inspecciones"]]
    elif rol == "miembro":
        modulos = [m for m in modulos_base if m[1] == "documentos"]
    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # ======================================================
    # 🔲 GRID DE MÓDULOS
    # ======================================================
    cols = st.columns(3)
    for i, (texto, modulo, css_id) in enumerate(modulos):
        with cols[i % 3]:
            button_clicked = st.button(texto, key=f"btn_{modulo}")
            st.markdown(f"<div id='{css_id}'></div>", unsafe_allow_html=True)
            if button_clicked:
                st.session_state["go_to_page"] = modulo
                st.rerun()

    # ======================================================
    # 🔒 CERRAR SESIÓN
    # ======================================================
    st.write("---")
    logout = st.button("🔒 Cerrar sesión", key="logout")
    st.markdown("<div id='logout_btn'></div>", unsafe_allow_html=True)

    if logout:
        st.session_state.clear()
        st.rerun()
