import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return 

    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)
    
    modulos = [] # Inicializar módulos
    
    # ---------------------------------------
    # CONFIGURAR MÓDULOS Y COLORES
    # ---------------------------------------
    modulos_base = [
        ("📁", "Gestión de Proyectos", "proyectos", "#AEDFF7", "#C9B2D9"),
        ("👥", "Gestión de Usuarios", "registrar_miembros", "#F7DCC4", "#F4CDB3"),
        ("🧾", "Inspecciones y Evaluaciones", "inspecciones", "#BEE4DD", "#A6D9D0"),
        ("📄", "Gestión Documental", "documentos", "#C9B2D9", "#F7DCC4"),
        ("📊", "Reportes", "reportes", "#A6D9D0", "#DCC8E3"),
        ("⚙️", "Configuración", "configuracion", "#F4CDB3", "#BEE4DD"),
    ]
    
    if rol == "institucional":
        modulos = modulos_base
    elif rol == "promotor":
        modulos = [m for m in modulos_base if m[2] in ["proyectos", "inspecciones"]]
    elif rol == "miembro":
        modulos = [m for m in modulos_base if m[2] in ["documentos"]]

    if not modulos:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados en este momento.")
        return

    # ---------------------------------------
    # CSS GENERAL PARA LOS CONTENEDORES DE TARJETA Y EL DISEÑO
    # ---------------------------------------
    st.markdown("""
<style>
/* Estilos para el contenedor de Streamlit que actuará como la tarjeta */
/* Usamos el ID generado por Streamlit para apuntar al st.container */
.st-emotion-cache-1r6dm7m.eczf16g1 { /* Este selector puede variar, verificar en el navegador */
    padding: 0 !important; /* Elimina padding interno del contenedor */
    margin: 0 !important; /* Elimina margen interno del contenedor */
}

/* Estilos de la tarjeta (aplicado al contenedor del botón) */
.card-container {
    height: 150px; 
    width: 100%;  
    border-radius: 18px;
    margin-bottom: 18px;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 4px 18px rgba(0,0,0,0.15);
    transition: 0.25s ease-in-out;
    cursor: pointer; /* Cursor de puntero para el contenedor */
    position: relative; /* Necesario para posicionar el botón interno */
    display: flex; /* Para centrar el contenido (botón) */
    justify-content: center;
    align-items: center;
    overflow: hidden; /* Asegura que nada se salga de los bordes redondeados */
}

.card-container:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 24px rgba(0,0,0,0.20);
}

/* 🚨 Estilos para el botón Streamlit INTERNO (hijo del contenedor .card-container) */
/* Lo hacemos transparente y lo estiramos para que ocupe todo el contenedor */
.card-container > [data-testid="stButton"] > button {
    background: transparent !important; /* Transparente para ver el degradado del contenedor */
    border: none !important; /* Sin borde */
    color: transparent !important; /* Oculta el label de espacio */
    height: 100% !important; /* Ocupa toda la altura del contenedor */
    width: 100% !important; /* Ocupa todo el ancho del contenedor */
    position: absolute !important; /* Se posiciona sobre todo el contenedor */
    top: 0;
    left: 0;
    z-index: 30; /* Asegura que esté por encima de la capa de diseño */
}

/* Estilos de la capa de diseño (icono y texto) */
.card-design-layer {
    position: absolute; /* Posicionamiento absoluto dentro del .card-container */
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: #4C3A60; 
    font-size: 16px; 
    font-weight: 700;
    z-index: 20; /* Por debajo del botón transparente */
    pointer-events: none !important; /* CRÍTICO: Permite que el clic atraviese */
}
.icono-grande {
    font-size: 42px;
    margin-bottom: 6px;
    display: block; 
    pointer-events: none !important; 
}
</style>
""", unsafe_allow_html=True)

    # ---------------------------------------
    # GRID DE BOTONES
    # ---------------------------------------
    cols = st.columns(3)
    
    for i, (icono, texto, modulo, color1, color2) in enumerate(modulos):
        
        def on_button_click(target_module):
            st.session_state.page = target_module
            st.rerun()

        with cols[i % 3]:
            # Contenedor para la tarjeta (aquí aplicamos el estilo de tarjeta y el degradado)
            card_html_id = f"card_container_{modulo}"
            
            st.markdown(f"""
                <div class="card-container" id="{card_html_id}" 
                     style="background: linear-gradient(135deg, {color1}, {color2});">
                    
                    <div class="card-design-layer">
                        <span class="icono-grande">{icono}</span>
                        <span style='display: block;'>{texto}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Ahora, el st.button va justo después y lo estiramos con CSS para que ocupe el contenedor anterior
            if st.button(
                label=" ", # Label vacío, el diseño lo provee el HTML
                key=f"button_{modulo}", # Cambiamos la key para no confundir con el id del div
                on_click=on_button_click,
                args=(modulo,), 
            ):
                pass
            
            # 🚨 JavaScript para posicionar el botón de Streamlit sobre el div HTML
            st.markdown(f"""
                <script>
                    const cardDiv = window.parent.document.getElementById('{card_html_id}');
                    const stButton = window.parent.document.querySelector('button[key="button_{modulo}"]').closest('[data-testid="stButton"]');

                    if (cardDiv && stButton) {{
                        // Mueve el contenedor del botón Streamlit para que esté DENTRO del div de la tarjeta
                        cardDiv.appendChild(stButton);
                    }}
                </script>
            """, unsafe_allow_html=True)


    st.write("---") 
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
