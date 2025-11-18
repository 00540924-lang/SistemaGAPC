import streamlit as st

def mostrar_menu():
    # ... (código para definir rol y módulos omitido) ...
    # Asegúrate de que tu definición de módulos incluya los colores: (Icono, Texto, Key, Color1, Color2)
    # Ejemplo:
    modulos_base = [
        ("📁", "Gestión de Proyectos", "proyectos", "#AEDFF7", "#C9B2D9"),
        # ... (resto de módulos) ...
    ]
    
    # ... (Lógica para asignar 'modulos' según el rol) ...

    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # 🚨 BLOQUE CSS CORREGIDO 🚨
    st.markdown("""
<style>
/* 1. Estilos base para el botón Streamlit (contenedor data-testid) */
[data-testid="stButton"] > button {
    /* **CRÍTICO:** Forzar el tamaño de la tarjeta para que no sean barras verticales */
    height: 150px;
    width: 100%; 
    border-radius: 18px;
    
    /* Mantenemos el resto de estilos */
    color: #4C3A60;
    font-size: 16px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    margin-bottom: 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.15);
    transition: 0.25s ease-in-out;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 10px;

    /* Intentamos de nuevo ocultar el botón nativo. Si falla, al menos tendrá forma de tarjeta */
    /* background: transparent; 
    border: none; */
}

/* 2. Estilos hover */
[data-testid="stButton"] > button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 24px rgba(0,0,0,0.20);
}

/* 3. Estilos de la capa de diseño (st.markdown) */
.card-design-layer {
    position: relative;
    z-index: 10;
    pointer-events: none; 
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
    pointer-events: none; 
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
            # 1. Contenido HTML del diseño
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
                /* Aseguramos que el diseño se superponga perfectamente */
                [data-testid="stVerticalBlock"] > div > div:nth-child({(i%3) * 2 + 1}) > div:nth-child(1) {{
                    margin-bottom: -150px; 
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
