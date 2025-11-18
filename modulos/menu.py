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

    # Tarjeta encabezado
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
    # ESTILOS CSS PARA TARJETAS
    # ---------------------------------------
    st.markdown("""
    <style>
    .cards-row { 
        display:flex; 
        justify-content:center; 
        gap:20px; 
        flex-wrap:wrap; 
        margin-top:15px; 
    }
    .card {
        width:150px; 
        height:150px; 
        border-radius:16px; 
        padding:18px;
        background: linear-gradient(135deg, #7B4397, #DC2430);
        color:white; 
        display:flex; 
        flex-direction:column; 
        justify-content:center; 
        align-items:center;
        font-weight:700; 
        font-size:50px; 
        text-align:center; 
        box-shadow:0 6px 18px rgba(0,0,0,0.12);
        transition: transform 0.18s ease, box-shadow 0.18s ease; 
        cursor:pointer;
    }
    .card:hover { 
        transform:translateY(-8px) scale(1.03); 
        box-shadow:0 12px 30px rgba(0,0,0,0.20); 
    }
    .card-icon {
        font-size:55px;
        margin-bottom:8px;
    }
    .card-sub { 
        font-size:15px; 
        font-weight:600; 
        opacity:0.95; 
    }
    a {
        text-decoration:none;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------
    # GENERAR TARJETAS CON ENLACES <a>
    # ---------------------------------------
    html_cards = "<div class='cards-row'>"

    for icono, texto, modulo in modulos:
        # CORRECCIÓN: Se envuelve el DIV de la tarjeta dentro del tag <a>
        # para que se apliquen los estilos CSS y funcione el enlace.
        html_cards += f"""
            <a href='?modulo={modulo}'>
                <div class='card'>
                    <div class='card-icon'>{icono}</div>
                    <div class='card-sub'>{texto}</div>
                </div>
            </a>
        """

    html_cards += "</div>"
    st.markdown(html_cards, unsafe_allow_html=True)

    # ---------------------------------------
    # BOTÓN CERRAR SESIÓN
    # ---------------------------------------
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("🔒 Cerrar sesión", key="cerrar_sesion_btn"):
            st.session_state.clear()
            st.rerun()
