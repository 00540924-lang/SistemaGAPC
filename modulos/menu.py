import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # -----------------------------------------------------
    # CSS CORRECTO: COLOR + ANIMACIÓN POR MÓDULO
    # -----------------------------------------------------
    st.markdown("""
    <style>

    /* ESTILO GENERAL */
    .menu-btn {
        color: white !important;
        border-radius: 12px !important;
        padding: 20px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        width: 100% !important;
        height: 110px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    }

    .menu-btn:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
    }

    /* 🎨 COLORES POR CLASE */
    .btn-proyectos      { background-color: #F4B400 !important; }
    .btn-usuarios       { background-color: #8E24AA !important; }
    .btn-inspecciones   { background-color: #E53935 !important; }
    .btn-documentos     { background-color: #1E88E5 !important; }
    .btn-reportes       { background-color: #43A047 !important; }
    .btn-configuracion  { background-color: #6D4C41 !important; }

    /* BOTÓN CERRAR SESIÓN */
    .logout-btn {
        background-color: #424242 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 12px 22px !important;
        font-size: 16px !important;
        width: 200px !important;
        transition: transform 0.2s ease !important;
    }

    .logout-btn:hover {
        transform: scale(1.05) !important;
        background-color: #000000 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # TÍTULO
    # -----------------------------------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # MÓDULOS BASE: TEXTO, PAGE, CLASE CSS
    # -----------------------------------------------------
    modulos_base = [
        ("📁 Gestión de Proyectos", "proyectos", "btn-proyectos"),
        ("👥 Gestión de Usuarios", "registrar_miembros", "btn-usuarios"),
        ("📝 Inspecciones y Evaluaciones", "inspecciones", "btn-inspecciones"),
        ("📄 Gestión Documental", "documentos", "btn-documentos"),
        ("📊 Reportes", "reportes", "btn-reportes"),
        ("⚙️ Configuración", "configuracion", "btn-configuracion"),
    ]

    # -----------------------------------------------------
    # LÓGICA DE ROLES
    # -----------------------------------------------------
    if rol == "institucional":
        modulos = modulos_base
    elif rol == "promotor":
        modulos = [m for m in modulos_base if m[1] in ["proyectos", "inspecciones"]]
    elif rol == "miembro":
        modulos = [m for m in modulos_base if m[1] == "documentos"]
    else:
        st.warning("⚠️ Este rol no tiene módulos asignados.")
        return

    # -----------------------------------------------------
    # GRID DE BOTONES
    # -----------------------------------------------------
    cols = st.columns(3)

    for i, (texto, modulo, css_class) in enumerate(modulos):
        with cols[i % 3]:

            # Creamos un botón invisible
            clicked = st.button(texto, key=f"btn_{modulo}")

            # Insertamos CSS directo al botón recién creado
            st.markdown(
                f"""
                <script>
                    var btn = document.querySelector('button[k='{f"btn_{modulo}"}']');
                    if (btn) {{
                        btn.classList.add('menu-btn');
                        btn.classList.add('{css_class}');
                    }}
                </script>
                """,
                unsafe_allow_html=True
            )

            if clicked:
                st.session_state.page = modulo
                st.rerun()

    # -----------------------------------------------------
    # CERRAR SESIÓN
    # -----------------------------------------------------
    st.write("---")
    logout = st.button("🔒 Cerrar sesión", key="logout")

    st.markdown("""
        <script>
            var l = document.querySelector('button[k="logout"]');
            if (l) { l.classList.add('logout-btn'); }
        </script>
        """,
        unsafe_allow_html=True
    )

    if logout:
        st.session_state.clear()
        st.rerun()

