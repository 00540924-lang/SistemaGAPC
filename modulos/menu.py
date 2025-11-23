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
/* Botones de módulos grandes */
div.row-widget.stButton > button {
    width: 240px !important;
    height: 90px !important;
    padding: 0 !important;
    margin: 8px !important;

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

div.row-widget.stButton > button:hover {
    transform: scale(1.07) !important;
    box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
}

/* Colores específicos para cada botón usando keys únicos */
button[key='btn_credenciales'] { background-color: #F4B400 !important; }
button[key='btn_registrar_miembros'] { background-color: #8E24AA !important; color: white !important; }
button[key='btn_grupos'] { background-color: #E53935 !important; color: white !important; }
button[key='btn_reglamento'] { background-color: #1E88E5 !important; color: white !important; }
button[key='btn_reportes'] { background-color: #43A047 !important; color: white !important; }
button[key='btn_multas'] { background-color: #6D4C41 !important; color: white !important; }
button[key='btn_asistencia'] { background-color: #FF7043 !important; color: white !important; }
button[key='btn_GAPC'] { background-color: #29B6F6 !important; color: white !important; }
button[key='btn_prestamos'] { background-color: #9C27B0 !important; color: white !important; }
button[key='btn_caja'] { background-color: #00BFA5 !important; color: white !important; }
button[key='btn_ahorro_final'] { background-color: #FF9800 !important; color: white !important; }
button[key='btn_reuniones'] { background-color: #FF5252 !important; color: white !important; }

/* Botón de cerrar sesión más pequeño */
button[key='logout'] {
    width: 160px !important;
    height: 50px !important;
    background-color: #424242 !important;
    color: white !important;
    border-radius: 8px !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    transition: transform 0.2s ease !important;
    margin: 0 auto !important;
    display: block !important;
}

button[key='logout']:hover {
    transform: scale(1.05) !important;
    background-color: #000000 !important;
}

/* Contenedor centrado para el botón de logout */
div[data-testid='stVerticalBlock'] > div:has(button[key='logout']) {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}
</style>
""", unsafe_allow_html=True)

    # -----------------------------------------------------
    #                    TÍTULO
    # -----------------------------------------------------
    st.markdown("<h1 style='text-align:center;color:#4C3A60;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # -----------------------------------------------------
    #        MOSTRAR USUARIO Y TEXTO SEGÚN ROL
    # -----------------------------------------------------
    st.markdown(
        f"<p style='text-align:center; font-size:18px; color:#4C3A60;'>Usuario: {st.session_state['usuario']}</p>",
        unsafe_allow_html=True
    )

    # Estilo destacado para Desarrollador, Promotor e Institucional
    rol_l = rol.lower()
    
    if usuario == "dark":
        st.markdown(
            "<p style='text-align:center; font-size:16px; color:#FF5722; font-weight:bold;'>Desarrollador</p>",
            unsafe_allow_html=True
        )
    elif rol_l == "promotor":
        st.markdown(
            "<p style='text-align:center; font-size:16px; color:#3F51B5; font-weight:bold;'>Promotor</p>",
            unsafe_allow_html=True
        )
    elif rol_l == "institucional":
        st.markdown(
            "<p style='text-align:center; font-size:16px; color:#2E7D32; font-weight:bold;'>Institucional</p>",
            unsafe_allow_html=True
        )
    elif st.session_state.get("nombre_grupo"):
        st.markdown(
            f"<p style='text-align:center; font-size:16px; color:#6D4C41;'>Grupo: {st.session_state['nombre_grupo']}</p>",
            unsafe_allow_html=True
        )

    # -----------------------------------------------------
    #                   MÓDULOS BASE
    # -----------------------------------------------------
    modulos_base = [
        ("📁 Credenciales", "credenciales"),
        ("👥 Gestión de Miembros", "registrar_miembros"),
        ("📝 Grupos", "grupos"),
        ("📜 Reglamento", "reglamento"),
        ("📊 Reportes", "reportes"),
        ("💸 Multas", "multas"),
        ("📋 Asistencia", "asistencia"),
        ("🏛️ GAPC", "GAPC"),
        ("💼 Préstamos", "prestamos"),
        ("💰 Caja", "caja"),
        ("💾 Ahorro", "ahorro_final"),
        ("📌 Reuniones", "reuniones"),
    ]

    # -----------------------------------------------------
    #          FILTRO POR ROL
    # -----------------------------------------------------
    if usuario == "dark":
        modulos = modulos_base
    elif rol_l == "institucional":
        modulos = [m for m in modulos_base if m[1] not in ["caja","multas","prestamos","reglamento","asistencia","registrar_miembros","reuniones","ahorro_final"]]
    elif rol_l == "promotor":
        modulos = [m for m in modulos_base if m[1] in ["credenciales", "grupos"]]
    elif rol_l == "miembro":
        modulos = [m for m in modulos_base if m[1] in ["reglamento", "caja", "multas", "prestamos", "ahorro_final", "reuniones","ahorro_final","registrar_miembros"]]
    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # -----------------------------------------------------
    #               GRID DE BOTONES
    # -----------------------------------------------------
    cols = st.columns(3)

    for i, (texto, modulo) in enumerate(modulos):
        with cols[i % 3]:
            if st.button(texto, key=f"btn_{modulo}"):
                st.session_state.page = modulo
                st.rerun()
                return

    # -----------------------------------------------------
    #               BOTÓN CERRAR SESIÓN (MÁS PEQUEÑO)
    # -----------------------------------------------------
    st.write("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔒 Cerrar sesión", key="logout"):
            st.session_state.clear()
            st.rerun()
