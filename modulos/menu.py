import streamlit as st

def mostrar_menu():

    # ---------------------------------------
    # LEER ROL DEL USUARIO DESDE EL LOGIN
    # ---------------------------------------
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        st.stop()

    # ---------------------------------------
    # CONFIGURAR MÓDULOS SEGÚN ROL
    # ---------------------------------------
    modulos = []

    if rol == "institucional":
        modulos = [
            ("📁", "Gestión de Proyectos", "proyectos"),
            ("👥", "Gestión de Usuarios", "usuarios"),
            ("🧾", "Inspecciones y Evaluaciones", "inspecciones"),
            ("📄", "Gestión Documental", "documentos"),
            ("📊", "Reportes", "reportes"),
            ("⚙️", "Configuración", "configuracion"),
        ]

    elif rol == "promotor":
        modulos = [
            ("📁", "Gestión de Proyectos", "proyectos"),
            ("🧾", "Inspecciones y Evaluaciones", "inspecciones"),
        ]

    elif rol == "miembro":
        modulos = [
            ("📄", "Gestión Documental", "documentos"),
        ]

    else:
        st.error("❌ Rol no reconocido.")
        st.stop()

    # ---------------------------------------
    # TÍTULO
    # ---------------------------------------
    st.markdown("""
        <h1 style='text-align:center; color:#4C3A60; font-size: 36px; margin-bottom:4px'>
            Menú Principal – GAPC
        </h1>
        """, unsafe_allow_html=True)

    # Tarjeta
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #B7A2C8, #F7C9A4);
            padding: 3px;
            border-radius: 12px;
            color: #4C3A60;
            font-size: 18px;
            text-align: center;
            width: 80%;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
            margin: auto;
        ">
            <b>Seleccione un módulo para continuar</b><br>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------
    # TARJETAS GENERADAS POR EL ROL
    # ---------------------------------------
    st.markdown("""
        <style>
        .cards-row { display:flex; justify-content:center; gap:20px; flex-wrap:wrap; margin-top:15px; }
        .card {
            width:150px; height:150px; border-radius:16px; padding:18px;
            color:white; display:flex; flex-direction:column; justify-content:center; align-items:center;
            font-weight:700; font-size:50px; text-align:center; box-shadow:0 6px 18px rgba(0,0,0,0.12);
            transition: transform 0.18s ease, box-shadow 0.18s ease; cursor:pointer;
        }
        .card:hover { transform:translateY(-8px) scale(1.03); box-shadow:0 12px 30px rgba(0,0,0,0.20); }
        .card-sub { font-size:15px; font-weight:600; opacity:0.95; margin-top:0.2px; }
        </style>
        """, unsafe_allow_html=True)

    html_cards = "<div class='cards-row'>"

    for icono, texto, modulo in modulos:
        html_cards += f"""
            <div class='card' onclick="window.location.href='?modulo={modulo}'">
                {icono}
                <div class='card-sub'>{texto}</div>
            </div>
        """

    html_cards += "</div>"

    st.markdown(html_cards, unsafe_allow_html=True)

    # ---------------------------------------
    # BOTÓN DE CERRAR SESIÓN
    # ---------------------------------------
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        if st.button("🔒 Cerrar sesión", key="cerrar_sesion_btn"):
            st.session_state.clear()
            st.rerun()
