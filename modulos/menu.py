import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        st.stop()

    # --- DEFINICIÓN DE MÓDULOS (código omitido) ---
    if rol == "institucional":
        modulos = [
            ("📁", "Gestión de Proyectos", "proyectos"),
            ("👥", "Gestión de Usuarios", "registrar_miembros"),
            ("🧾", "Inspecciones y Evaluaciones", "inspecciones"),
            ("📄", "Gestión Documental", "documentos"),
            ("📊", "Reportes", "reportes"),
            ("⚙️", "Configuración", "configuracion"),
        ]
    # ... (otros roles) ...

    # ---------------------------------------
    # TÍTULO Y CSS
    # ---------------------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # 🚨 CSS: Aseguramos el estilo y el layout para el botón Streamlit
    st.markdown("""
<style>
/* 1. Estilos base para el contenedor del botón Streamlit */
/* Necesitamos forzar la altura y el padding para que parezca una tarjeta */
[data-testid^="stButton"] > button {
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
    /* Aseguramos que el contenido HTML interno se centre */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

/* 2. Estilos hover */
[data-testid^="stButton"] > button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 24px rgba(0,0,0,0.20);
}

/* 3. Estilos de íconos/texto internos */
.icono-grande {
    font-size: 42px;
    margin-bottom: 6px;
}

/* 4. Estilos de color (Aplicados por llave 'key' para ser específicos) */
[data-testid="stButton"] button[key="card_proyectos"] { background: linear-gradient(135deg, #AEDFF7, #C9B2D9); }
[data-testid="stButton"] button[key="card_registrar_miembros"] { background: linear-gradient(135deg, #F7DCC4, #F4CDB3); }
[data-testid="stButton"] button[key="card_inspecciones"] { background: linear-gradient(135deg, #BEE4DD, #A6D9D0); }
[data-testid="stButton"] button[key="card_documentos"] { background: linear-gradient(135deg, #C9B2D9, #F7DCC4); }
[data-testid="stButton"] button[key="card_reportes"] { background: linear-gradient(135deg, #A6D9D0, #DCC8E3); }
[data-testid="stButton"] button[key="card_configuracion"] { background: linear-gradient(135deg, #F4CDB3, #BEE4DD); }
</style>
""", unsafe_allow_html=True)

    # ---------------------------------------
    # GRID DE BOTONES
    # ---------------------------------------
    cols = st.columns(3)

    for i, (icono, texto, modulo) in enumerate(modulos):
        
        # Función de callback para el botón
        def on_button_click(target_module):
            st.session_state.page = target_module
            st.rerun()

        with cols[i % 3]:
            # Usamos el componente st.button directamente
            # El label contiene el HTML, que Streamlit sí permite si no se usa unsafe_allow_html=True en el st.button.
            # Sin embargo, dado que queremos HTML en el label, debemos usar un truco:
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <span class="icono-grande">{icono}</span>
                    {texto}
                </div>
            """, unsafe_allow_html=True)
            
            # El botón real de Streamlit que se encuentra DENTRO del st.markdown
            # Usamos un label vacío o un espacio, y la lógica de click.
            if st.button(
                label=" ", # Label simple, para evitar el TypeError
                key=f"card_{modulo}",
                on_click=on_button_click,
                args=(modulo,), 
            ):
                pass
            
            # 🚨 INYECCIÓN DE CSS ESPECÍFICO PARA POSICIONAMIENTO
            # Este es el truco más crucial. Debemos posicionar el HTML del diseño
            # sobre el botón Streamlit y aplicar el color.
            st.markdown(f"""
                <style>
                /* Ocultar el espacio extra que crea st.markdown */
                div[data-testid="stVerticalBlock"] > div:nth-child({(i%3) * 2 + 1}) > div:nth-child(2) > div {{
                    margin-top: -150px; /* Mueve el botón Streamlit hacia arriba, superponiéndolo al HTML */
                }}
                /* Aplicar los estilos de color directamente al botón */
                [data-testid="stButton"] button[key="card_{modulo}"] {{ 
                    background: linear-gradient(135deg, 
                        {modulos[i%6][1]} 
                        /* Deberías definir los colores en una lista o diccionario para que sean dinámicos aquí */
                    ); 
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
