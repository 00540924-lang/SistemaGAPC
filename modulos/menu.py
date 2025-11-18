import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)
    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # CSS para botones visuales con colores distintos
    st.markdown("""
    <style>
    .menu-btn {
        display: inline-block;
        width: 240px;
        height: 90px;
        line-height: 90px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 18px;
        color: white;
        text-align: center;
        margin: 8px 8px;
        cursor: pointer;
        user-select: none;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .menu-btn:hover {
        transform: scale(1.07);
        box-shadow: 0 10px 22px rgba(0,0,0,0.3);
    }
    .proyectos { background-color: #F4B400; color: #4C3A60; }
    .usuarios { background-color: #8E24AA; }
    .grupos { background-color: #E53935; }
    .documentos { background-color: #1E88E5; }
    .reportes { background-color: #43A047; }
    .configuracion { background-color: #6D4C41; }
    #logout_btn {
        width: 200px;
        height: 60px;
        background-color: #424242;
        color: white;
        border-radius: 10px;
        font-weight: 600;
        font-size: 16px;
        margin-top: 30px;
        cursor: pointer;
        transition: transform 0.2s ease;
        display: inline-block;
        text-align: center;
        line-height: 60px;
        user-select: none;
    }
    #logout_btn:hover {
        transform: scale(1.05);
        background-color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    modulos = []
    if rol == "institucional":
        modulos = [
            ("📁 Gestión de Proyectos", "proyectos", "proyectos"),
            ("👥 Gestión de Usuarios", "registrar_miembros", "usuarios"),
            ("📝 Grupos", "grupos", "grupos"),
            ("📄 Gestión Documental", "documentos", "documentos"),
            ("📊 Reportes", "reportes", "reportes"),
            ("⚙️ Configuración", "configuracion", "configuracion"),
        ]
    elif rol == "promotor":
        modulos = [
            ("📁 Gestión de Proyectos", "proyectos", "proyectos"),
            ("📝 Grupos", "grupos", "grupos"),
        ]
    elif rol == "miembro":
        modulos = [
            ("📄 Gestión Documental", "documentos", "documentos"),
        ]
    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    cols = st.columns(3)
    for i, (texto, modulo, clase) in enumerate(modulos):
        with cols[i % 3]:
            # Botón visual (HTML) que "simula" un botón con estilos y captura clicks con st.button oculto
            btn_html = f'<div class="menu-btn {clase}">{texto}</div>'
            st.markdown(btn_html, unsafe_allow_html=True)
            if st.button(f"btn_{modulo}", key=f"btn_{modulo}", help=texto):
                st.session_state.page = modulo
                st.experimental_rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # Botón logout estilo similar
    st.markdown('<div id="logout_btn">🔒 Cerrar sesión</div>', unsafe_allow_html=True)
    if st.button("logout_btn", key="logout"):
        st.session_state.clear()
        st.experimental_rerun()
