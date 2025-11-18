import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        st.stop()

    # ---------------------------------------
    # CONFIGURAR MÓDULOS SEGÚN ROL
    # ---------------------------------------
    if rol == "institucional":
        modulos = [
            ("📁", "Gestión de Proyectos", "proyectos", "#AEDFF7", "#C9B2D9"),
            ("👥", "Gestión de Usuarios", "registrar_miembros", "#F7DCC4", "#F4CDB3"),
            ("🧾", "Inspecciones y Evaluaciones", "inspecciones", "#BEE4DD", "#A6D9D0"),
            ("📄", "Gestión Documental", "documentos", "#C9B2D9", "#F7DCC4"),
            ("📊", "Reportes", "reportes", "#A6D9D0", "#DCC8E3"),
            ("⚙️", "Configuración", "configuracion", "#F4CDB3", "#BEE4DD"),
        ]

    elif rol == "promotor":
        modulos = [
            ("📁", "Gestión de Proyectos", "proyectos", "#AEDFF7", "#C9B2D9"),
            ("🧾", "Inspecciones y Evaluaciones", "inspecciones", "#BEE4DD", "#A6D9D0"),
        ]

    elif rol == "miembro":
        modulos = [
            ("📄", "Gestión Documental", "documentos", "#C9B2D9", "#F7DCC4"),
        ]
        
    # ---------------------------------------
    # TÍTULO Y CSS
    # ---------------------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # 🚨 CSS: Aplicamos el estilo de tarjeta y el degradado de color
    st.markdown("""
<style>
/* 1. Estilos base para el botón Streamlit (contenedor data-testid) */
/* El selector apunta al botón real dentro del contenedor */
[data-testid="stButton"] > button {
    height: 150px;
    width: 100%;
    border-radius: 18px;
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
    /* Forzar que el contenido (HTML inyectado) se centre */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 10px; /* Ajuste del padding */
}

/* 2. Estilos hover */
[data-testid="stButton"] > button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 24px rgba(0,0,0,0.20);
}

/* 3. Estilos de íconos/texto internos */
.icono-grande {
    font-size: 42px;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

    # ---------------------------------------
    # GRID DE BOTONES
    # ---------------------------------------
    cols = st.columns(3)

    for i, (icono, texto, modulo, color1, color2) in enumerate(modulos):
        
        # Función de callback de Streamlit
        def on_button_click(target_module):
            st.session_state.page = target_module
            st.rerun()

        with cols[i % 3]:
            # 1. Creamos el contenido HTML del botón
            button_content = f"""
                <span class="icono-grande">{icono}</span>
                <span style='text-align:center;'>{texto}</span>
            """
            
            # 2. Inyectamos CSS específico para el color del botón
            # Usamos el KEY del botón para apuntar exactamente a ese widget
            st.markdown(f"""
                <style>
                [data-testid="stButton"] button[key="card_{modulo}"] {{
                    background: linear-gradient(135deg, {color1}, {color2});
                }}
                </style>
            """, unsafe_allow_html=True)

            # 3. Usamos el componente st.button (con un truco para el HTML)
            # Como Streamlit ya no acepta HTML en el label, inyectamos el HTML ANTES
            # y usamos un botón que no tiene label, dejando que el CSS lo posicione.
            
            # Usamos un truco: inyectamos el HTML del icono y texto y luego un botón con un label simple
            st.markdown(button_content, unsafe_allow_html=True)
            
            # Botón Streamlit real con la lógica (label vacío)
            if st.button(
                label=" ", # ¡Label vacío! Es CRUCIAL
                key=f"card_{modulo}",
                on_click=on_button_click,
                args=(modulo,), 
            ):
                pass
            
            # 🚨 El truco final: usamos CSS para mover el contenido HTML sobre el botón nativo
            st.markdown(f"""
                <style>
                /* Selecciona el bloque vertical (contenedor) y mueve el HTML hacia el botón */
                [data-testid="stVerticalBlock"] > div:nth-child({(i % 3) * 2 + 1}) > div:nth-child(1) {{
                    margin-bottom: -150px; /* Mueve el diseño de texto y icono hacia abajo, sobre el botón vacío */
                    pointer-events: none; /* Crucial: permite que el clic atraviese este HTML y llegue al botón */
                }}
                </style>
            """, unsafe_allow_html=True)


    # ---------------------------------------
    # BOTÓN CERRAR SESIÓN
    # ---------------------------------------
    st.write("") 
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
