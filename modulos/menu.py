import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        # Opcionalmente, puedes redirigir al login si no hay rol
        st.session_state.page = "login"
        st.rerun()
        st.stop()
        return

    # -----------------------------------------------------
    #       🎨 CSS - Botones con animación + colores (Corregido)
    # -----------------------------------------------------
    st.markdown("""
<style>

/* --- 1. Estilos Base --- */
/* Estilo para centrar el div.stButton dentro de la columna */
div.stButton {
    display: flex !important;
    justify-content: center !important;
}

/* Estilo base de TODOS los botones */
div.stButton > button {
    width: 180px !important;    /* ← tamaño fijo horizontal */
    height: 100px !important;    /* ← tamaño fijo vertical */
    padding: 0 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    white-space: nowrap !important;     /* No permite que el texto salte de línea */
    overflow: hidden !important;        /* Evita que el texto desborde */
    text-overflow: ellipsis !important; /* Si el texto es largo → agrega "..." */

    font-size: 18px !important;
    font-weight: 600 !important;
    color: white !important; /* Texto blanco (para la mayoría de los fondos oscuros) */

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

/* --- 2. Colores Personalizados (Selector Agresivo con :has()) --- */
/* Este selector busca el contenedor del botón (div.stButton) que contiene el div con el ID inyectado. */

/* Gestión de Proyectos (Amarillo, requiere texto oscuro) */
[data-testid*="column"] > div > div:nth-child(1) > div.stButton:has(div#proyectos_btn) > button { 
    background-color: #F4B400 !important; 
    color: #4C3A60 !important; 
}
/* Gestión de Usuarios */
[data-testid*="column"] > div > div:nth-child(1) > div.stButton:has(div#usuarios_btn) > button { background-color: #8E24AA !important; }
/* Grupos */
[data-testid*="column"] > div > div:nth-child(1) > div.stButton:has(div#grupos_btn) > button { background-color: #E53935 !important; }
/* Gestión Documental */
[data-testid*="column"] > div > div:nth-child(1) > div.stButton:has(div#documentos_btn) > button { background-color: #1E88E5 !important; }
/* Reportes */
[data-testid*="column"] > div > div:nth-child(1) > div.stButton:has(div#reportes_btn) > button { background-color: #43A047 !important; }
/* Configuración */
[data-testid*="column"] > div > div:nth-child(1) > div.stButton:has(div#configuracion_btn) > button { background-color: #6D4C41 !important; }

/* --- 3. Logout --- */
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
    #                   GRID DE BOTONES 
    # -----------------------------------------------------
    cols = st.columns(3)

    for i, (texto, modulo, css_id) in enumerate(modulos):
        with cols[i % 3]:
            # 1. Creamos el botón
            b = st.button(texto, key=f"btn_{modulo}")

            # 2. Inyectamos el DIV vacío con el ID que el CSS agresivo buscará.
            st.markdown(f"<div id='{css_id}'></div>", unsafe_allow_html=True)

            # 3. Lógica de navegación - CORRECCIÓN DE ERROR DUPLICATE KEY
            if b:
                st.session_state.page = modulo
                st.rerun()
                st.stop() # Detiene la ejecución actual para evitar el error
    
    # -----------------------------------------------------
    #                   BOTÓN CERRAR SESIÓN 
    # -----------------------------------------------------
    st.write("---")

    logout = st.button("🔒 Cerrar sesión", key="logout")
    
    # Inyectamos el DIV para el botón de cerrar sesión
    st.markdown("<div id='logout_btn'></div>", unsafe_allow_html=True)

    if logout:
        st.session_state.clear()
        st.session_state.page = "login" 
        st.rerun()
        st.stop() # Detiene la ejecución actual para evitar el error

# -----------------------------------------------------
#                       EJEMPLO DE USO (para pruebas)
# -----------------------------------------------------
# La ejecución del script inicia aquí (app.py)

# Inicialización de la sesión
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'rol' not in st.session_state:
    st.session_state.rol = None 

# Lógica de renderizado de páginas
if st.session_state.page == 'menu':
    mostrar_menu()
    
elif st.session_state.page == 'login':
    st.title("Página de Login Simulada")
    st.markdown("Selecciona un rol para iniciar la sesión:")
    
    col_inst, col_prom, col_miem = st.columns(3)
    
    with col_inst:
        if st.button("Simular Login Institucional", key="login_inst"):
            st.session_state.rol = 'institucional'
            st.session_state.page = 'menu'
            st.rerun()
    with col_prom:
        if st.button("Simular Login Promotor", key="login_prom"):
            st.session_state.rol = 'promotor'
            st.session_state.page = 'menu'
            st.rerun()
    with col_miem:
        if st.button("Simular Login Miembro", key="login_miem"):
            st.session_state.rol = 'miembro'
            st.session_state.page = 'menu'
            st.rerun()
else:
    # Simulación de la página del módulo seleccionado
    st.header(f"Estás en el módulo: {st.session_state.page.replace('_', ' ').title()}")
    if st.button("← Volver al Menú Principal"):
        st.session_state.page = 'menu'
        st.rerun()
