import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        st.stop()

    # ---------------------------------------
    # CONFIGURAR MÓDULOS SEGÚN ROL (Añadimos los colores a la lista)
    # ---------------------------------------
    # Los colores deben estar en la lista para el CSS dinámico
    modulos_base = [
        ("📁", "Gestión de Proyectos", "proyectos", "#AEDFF7", "#C9B2D9"),
        ("👥", "Gestión de Usuarios", "registrar_miembros", "#F7DCC4", "#F4CDB3"),
        ("🧾", "Inspecciones y Evaluaciones", "inspecciones", "#BEE4DD", "#A6D9D0"),
        ("📄", "Gestión Documental", "documentos", "#C9B2D9", "#F7DCC4"),
        ("📊", "Reportes", "Reportes", "#A6D9D0", "#DCC8E3"),
        ("⚙️", "Configuración", "configuracion", "#F4CDB3", "#BEE4DD"),
    ]

    if rol == "institucional":
        modulos = modulos_base
    elif rol == "promotor":
        modulos = [m for m in modulos_base if m[2] in ["proyectos", "inspecciones"]]
    elif rol == "miembro":
        modulos = [m for m in modulos_base if m[2] in ["documentos"]]

    # ---------------------------------------
    # TÍTULO Y CSS
    # ---------------------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # Bloque CSS general (Estilos de Tarjeta y Layout)
    st.markdown("""
<style>
/* 1. Estilos base para el botón Streamlit (contenedor data-testid) */
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
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 10px;
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

/* 4. Selector para el st.markdown con el diseño: 
   Asegura que el diseño sea transparente al clic y se superponga */
.card-design-layer {
    position: relative;
    z-index: 10; /* Asegura que esté encima */
    pointer-events: none; /* PERMITE que el clic atraviese */
    text-align: center;
    width: 100%;
    /* Mueve el diseño hacia la izquierda para alinearlo en la columna */
    transform: translateX(-50%); 
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
            # 1. Contenido HTML del diseño
            button_content = f"""
                <div class="card-design-layer">
                    <span class="icono-grande">{icono}</span>
                    <span style='display: block;'>{texto}</span>
                </div>
            """
            
            # 2. Inyectamos el CSS de color y ajuste dinámico
            st.markdown(f"""
                <style>
                /* Aplica el color de fondo a la tarjeta (st.button) */
                [data-testid="stButton"] button[key="card_{modulo}"] {{
                    background: linear-gradient(135deg, {color1}, {color2});
                }}
                
                /* 🚨 Ajuste de Superposición: Mueve el diseño HTML de la tarjeta */
                /* Apuntamos al div que contiene el st.markdown */
                [data-testid="stVerticalBlock"] > div > div:nth-child({(i%3) + 1}) > div:nth-child(1) {{
                    margin-bottom: -150px; /* Mueve el diseño hacia abajo, sobre el botón */
                    position: relative;
                    z-index: 20; /* Más alto que el diseño */
                }}
                </style>
            """, unsafe_allow_html=True)

            # 3. Inyectamos el diseño HTML
            st.markdown(button_content, unsafe_allow_html=True)
            
            # 4. Botón Streamlit real con la lógica (label vacío)
            # Este es el elemento que debe recibir el clic
            if st.button(
                label=" ", 
                key=f"card_{modulo}",
                on_click=on_button_click,
                args=(modulo,), 
            ):
                pass
            
    # ---------------------------------------
    # BOTÓN CERRAR SESIÓN (Aseguramos que no se vea afectado por el CSS)
    # ---------------------------------------
    st.write("") 
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
