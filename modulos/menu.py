import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return # Simplemente retorna, no st.stop()

    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)
    
    # Inicializar módulos para evitar NameError
    modulos = []
    
    # ---------------------------------------
    # CONFIGURAR MÓDULOS Y COLORES
    # ---------------------------------------
    # Estructura de módulos: (Icono, Texto, Modulo Key, Color_Inicio, Color_Fin)
    modulos_base = [
        ("📁", "Gestión de Proyectos", "proyectos", "#AEDFF7", "#C9B2D9"),
        ("👥", "Gestión de Usuarios", "registrar_miembros", "#F7DCC4", "#F4CDB3"),
        ("🧾", "Inspecciones y Evaluaciones", "inspecciones", "#BEE4DD", "#A6D9D0"),
        ("📄", "Gestión Documental", "documentos", "#C9B2D9", "#F7DCC4"),
        ("📊", "Reportes", "reportes", "#A6D9D0", "#DCC8E3"),
        ("⚙️", "Configuración", "configuracion", "#F4CDB3", "#BEE4DD"),
    ]
    
    # Lógica de asignación de módulos
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
    # CSS PARA LOS BOTONES DE TARJETA
    # ---------------------------------------
    st.markdown("""
<style>
/* Estilos generales para CADA botón de Streamlit (el contenedor) */
[data-testid="stButton"] > button {
    height: 150px; /* Altura de la tarjeta */
    width: 100%; /* Ancho completo en la columna */
    border-radius: 18px; /* Bordes redondeados */
    color: #4C3A60; /* Color del texto */
    font-size: 16px; /* Tamaño de fuente */
    font-weight: 700; /* Negrita */
    border: none; /* Sin borde */
    cursor: pointer; /* Cursor de puntero */
    margin-bottom: 18px; /* Espacio entre tarjetas */
    backdrop-filter: blur(10px); /* Efecto Glassmorphism */
    -webkit-backdrop-filter: blur(10px); /* Para compatibilidad */
    box-shadow: 0 4px 18px rgba(0,0,0,0.15); /* Sombra */
    transition: 0.25s ease-in-out; /* Transición suave */
    
    /* Centrar el contenido HTML interno */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 10px; /* Espaciado interno */
}

/* Efecto hover */
[data-testid="stButton"] > button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 24px rgba(0,0,0,0.20);
}

/* Estilo para los iconos grandes */
.icono-grande {
    font-size: 42px;
    margin-bottom: 6px;
    display: block; /* Asegura que el icono esté en su propia línea */
}
</style>
""", unsafe_allow_html=True)

    # ---------------------------------------
    # GRID DE BOTONES
    # ---------------------------------------
    cols = st.columns(3)
    
    for i, (icono, texto, modulo, color1, color2) in enumerate(modulos):
        with cols[i % 3]:
            # Contenido HTML para el label del botón
            button_html_label = f"""
                <div style="text-align: center;">
                    <span class="icono-grande">{icono}</span>
                    <br>
                    <span>{texto}</span>
                </div>
            """
            
            # 🚨 Inyectamos CSS específico para el color de CADA botón
            st.markdown(f"""
                <style>
                [data-testid="stButton"] button[key="card_{modulo}"] {{
                    background: linear-gradient(135deg, {color1}, {color2});
                }}
                </style>
            """, unsafe_allow_html=True)

            # Usamos st.button directamente con el HTML en el label.
            # NOTA: Streamlit 1.27+ NO permite HTML inseguro en 'label'.
            # Para evitar el TypeError, usamos el truco de inyectar el HTML
            # y luego un botón con label vacío, y usamos CSS para superponer.
            
            # 1. Inyecta el diseño HTML
            st.markdown(button_html_label, unsafe_allow_html=True)

            # 2. Inyecta un botón Streamlit con label vacío y funcionalidad
            if st.button(
                label=" ", # Label vacío para evitar el TypeError
                key=f"card_{modulo}",
                on_click=lambda m=modulo: st.session_state.update(page=m, reran=True), # Usa lambda para pasar el argumento
                # args=(modulo,), # on_click no usa 'args' directamente si es lambda
            ):
                # La lógica de reran ya está en el lambda
                pass 
            
            # 3. 🚨 CSS para superponer el diseño sobre el botón vacío
            st.markdown(f"""
                <style>
                /* Este CSS mueve el diseño (st.markdown) sobre el botón (st.button) */
                [data-testid="stVerticalBlock"] > div > div:nth-child({(i%3) * 2 + 1}) > div:nth-child(1) {{
                    margin-bottom: -150px; /* Ajusta este valor si la superposición no es perfecta */
                    position: relative;
                    z-index: 10; /* Asegura que el diseño esté encima */
                    pointer-events: none; /* CRÍTICO: Permite que el clic atraviese el diseño */
                }}
                </style>
            """, unsafe_allow_html=True)


    st.write("---") # Separador
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
