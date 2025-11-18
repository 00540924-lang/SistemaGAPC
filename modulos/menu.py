import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # -----------------------------------------------------
    #       🎨 CSS - Botones con animación + colores
    # -----------------------------------------------------
    st.markdown("""
<style>

/* Estilo para centrar el div.stButton dentro de la columna */
div.stButton {
    display: flex !important;
    justify-content: center !important;
}

/* Estilo base de TODOS los botones */
div.stButton > button {
    width: 180px !important;
    height: 100px !important;
    padding: 0 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;

    font-size: 18px !important;
    font-weight: 600 !important;
    color: white !important; /* Blanco para fondos oscuros */

    border-radius: 12px !important;
    border: none !important;

    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
}

/* Hover */
div.stButton > button:hover {
    transform: scale(1.07) !important;
    box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
}

/* Colores personalizados - Apuntando al contenedor div.stButton por el ID inyectado */
/* ¡CORRECCIÓN! El color del texto es fundamental para el botón AMARILLO */
#proyectos_btn > button { 
    background-color: #F4B400 !important; 
    color: #4C3A60 !important; /* Texto oscuro para contrastar con el amarillo */
} 
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
    transition: transform 0.2s ease !important;
}
#logout_btn > button:hover {
    transform: scale(1.05) !important;
    background-color: #000000 !important;
}

</style>
""", unsafe_allow_html=True)

    # -----------------------------------------------------
    #                       TÍTULO
    # -----------------------------------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # -----------------------------------------------------
    #                       MÓDULOS BASE
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
    #                       FILTRO POR ROL
    # -----------------------------------------------------
    if rol == "institucional":
        modulos = modulos_base
    elif rol == "promotor":
        modulos = [m for m in modulos_base if m[1] in ["proyectos", "grupos"]]
    elif rol == "miembro":
        modulos = [m for m in modulos_base if m[1] == "documentos"]
    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # -----------------------------------------------------
    #                       GRID DE BOTONES (Solución robusta para colores)
    # -----------------------------------------------------
    cols = st.columns(3)

    for i, (texto, modulo, css_id) in enumerate(modulos):
        key = f"btn_{modulo}"
        with cols[i % 3]:
            # 1. Creamos el botón
            b = st.button(texto, key=key)

            # 2. Inyectamos JavaScript para encontrar el botón y poner el ID en su contenedor.
            # Este script es más fiable que buscar por data-testid
            st.markdown(f"""
                <script>
                    const key = "{key}";
                    // Busca el elemento del botón por su clave Streamlit
                    let buttonElement = window.parent.document.querySelector('[data-testid="stButton-{key}"]');
                    
                    if (buttonElement) {{
                        // Asigna el ID al contenedor padre (div.stButton)
                        buttonElement.parentElement.id = "{css_id}";
                    }}
                </script>
            """, unsafe_allow_html=True)

            # 3. Lógica de navegación
            if b:
                st.session_state.page = modulo
                st.rerun()

    # -----------------------------------------------------
    #                   BOTÓN CERRAR SESIÓN 
    # -----------------------------------------------------
    st.write("---")

    logout = st.button("🔒 Cerrar sesión", key="logout")
    
    # Inyectamos JavaScript para el botón de cerrar sesión
    st.markdown(f"""
        <script>
            let logout_button = window.parent.document.querySelector('[data-testid="stButton-logout"]');
            if (logout_button) {{
                logout_button.parentElement.id = "logout_btn";
            }}
        </script>
    """, unsafe_allow_html=True)

    if logout:
        st.session_state.clear()
        st.session_state.page = "login" 
        st.rerun()

# -----------------------------------------------------
#                       EJEMPLO DE USO (para pruebas)
# -----------------------------------------------------

if 'page' not in st.session_state:
    st.session_state.page = 'menu'
if 'rol' not in st.session_state:
    st.session_state.rol = 'institucional'

# Lógica de renderizado de páginas
if st.session_state.page == 'menu':
    mostrar_menu()
elif st.session_state.page == 'login':
    st.title("Página de Login Simulada")
    if st.button("Simular Inicio de Sesión como Institucional"):
        st.session_state.rol = 'institucional'
        st.session_state.page = 'menu'
        st.rerun()
else:
    st.header(f"Estás en el módulo: {st.session_state.page.replace('_', ' ').title()}")
    if st.button("← Volver al Menú Principal"):
        st.session_state.page = 'menu'
        st.rerun()
