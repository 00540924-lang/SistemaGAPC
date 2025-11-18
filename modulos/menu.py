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
    # CSS GENERAL PARA EL ESTILO DE LA TARJETA Y EL CLIC
    # ---------------------------------------
    st.markdown("""
<style>
/* 1. Estilos base para el botón Streamlit (Contenedor de la tarjeta) */
[data-testid="stButton"] > button {
    /* **CRÍTICO:** Forzar el tamaño y la forma de la tarjeta */
    height: 150px !important; 
    width: 100% !important;  
    border-radius: 18px;
    
    /* Estilos de tarjeta */
    color: #4C3A60;
    font-size: 16px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    margin-bottom: 18px;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 4px 18px rgba(0,0,0,0.15);
    transition: 0.25s ease-in-out;
    
    /* Centrar contenido (el label vacío " ") */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 10px;
}

/* 2. Estilos de la capa de diseño (st.markdown) */
.card-design-layer {
    position: relative;
    z-index: 10;
    /* 🚨 CRÍTICO: FORZAR PROPIEDAD PARA EL CLIC */
    pointer-events: none !important; 
    text-align: center;
    width: 100%;
    color: #4C3A60; 
    font-size: 16px; 
    font-weight: 700;
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
            # 1. Contenido HTML del diseño (Icono y Texto)
            button_design = f"""
                <div class="card-design-layer">
                    <span class="icono-grande">{icono}</span>
                    <span style='display: block;'>{texto}</span>
                </div>
            """
            
            # 2. Inyección de CSS para Color y Superposición
            st.markdown(f"""
                <style>
                /* Aplica el color de fondo a la tarjeta (st.button) */
                [data-testid="stButton"] button[key="card_{modulo}"] {{
                    background: linear-gradient(135deg, {color1}, {color2});
                }}
                
                /* 🚨 CRÍTICO: Superposición - Mueve el diseño HTML sobre el botón */
                /* Usamos el selector que apunta al div que contiene el st.markdown */
                [data-testid="stVerticalBlock"] > div > div:nth-child({(i%3) * 2 + 1}) > div:nth-child(1) {{
                    margin-bottom: -150px !important; /* Desplaza el diseño hacia abajo */
                    position: relative;
                    z-index: 20; 
                }}
                </style>
            """, unsafe_allow_html=True)

            # 3. Inyectamos el diseño HTML
            st.markdown(button_design, unsafe_allow_html=True)
            
            # 4. Botón Streamlit real con la lógica (label vacío)
            if st.button(
                label=" ", 
                key=f"card_{modulo}",
                on_click=on_button_click,
                args=(modulo,), 
            ):
                pass
            
    # ---------------------------------------
    # BOTÓN CERRAR SESIÓN
    # ---------------------------------------
    st.write("") 
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
