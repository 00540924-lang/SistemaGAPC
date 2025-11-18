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
            ("📁", "Gestión de Proyectos", "proyectos"),
            ("👥", "Gestión de Usuarios", "registrar_miembros"),
            ("🧾", "Inspecciones y Evaluaciones", "inspecciones"),
            ("📄", "Gestión Documental", "documentos"),
            ("📊", "Reportes", "reportes"),
            ("⚙️", "Configuración", "configuracion"),
        ]

    elif rol == "promotor":
        modulos = [
            ("📁", "Gestión de Proyectos", "proyectos"),
            ("🧾", "Inspecciones y Evaluaciones", "inspecciones"),
        ]

    elif rol == "miembro":
        modulos = [
            ("📄", "Gestión Documental", "documentos"),
        ]

    # ---------------------------------------
    # TÍTULO Y CSS
    # ---------------------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # 🚨 IMPORTANTE: Se elimina todo el CSS que ocultaba los botones de Streamlit,
    # y se enfoca el CSS en el estilo del botón HTML.
    st.markdown("""
<style>
/* Estilos existentes para las tarjetas */
.btn-glass {
    padding: 18px;
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
    text-align: center;
}
.btn-glass:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 24px rgba(0,0,0,0.20);
}
.icono-grande {
    font-size: 42px;
    margin-bottom: 6px;
}
.btn1 { background: linear-gradient(135deg, #AEDFF7, #C9B2D9); }
.btn2 { background: linear-gradient(135deg, #F7DCC4, #F4CDB3); }
.btn3 { background: linear-gradient(135deg, #BEE4DD, #A6D9D0); }
.btn4 { background: linear-gradient(135deg, #C9B2D9, #F7DCC4); }
.btn5 { background: linear-gradient(135deg, #A6D9D0, #DCC8E3); }
.btn6 { background: linear-gradient(135deg, #F4CDB3, #BEE4DD); }

/* Nuevo CSS: Oculta la columna de botones invisibles */
/* No es necesario si se elimina el st.button, pero a veces Streamlit añade wrappers */
/* Esto se soluciona eliminando el st.button y usando el callback en el HTML, como se muestra abajo */
</style>
""", unsafe_allow_html=True)

    # ---------------------------------------
    # GRID DE BOTONES
    # ---------------------------------------
    # Usaremos 3 columnas, pero sin el st.button invisible.
    cols = st.columns(3)

    for i, (icono, texto, modulo) in enumerate(modulos):
        clase_color = f"btn-glass btn{i+1}"
        
        # 1. Creamos una función de callback para el botón
        def on_button_click(target_module):
            st.session_state.page = target_module
            st.rerun()

        with cols[i % 3]:
            # 2. Usamos el componente st.button directamente con el estilo HTML
            # Este botón es la tarjeta completa y activa la función de cambio de página
            st.button(
                label=f"""
                    <span class="icono-grande">{icono}</span>
                    {texto}
                """,
                key=f"card_{modulo}",
                on_click=on_button_click,
                args=(modulo,),  # Pasa el nombre del módulo a la función on_click
                unsafe_allow_html=True,
                # 3. Aplicamos el estilo de la tarjeta directamente al botón
                help=f"Ir a {texto}",
            )
            
            # 4. Inyectamos el CSS de la tarjeta en el botón Streamlit
            # Buscamos la clase de Streamlit que envuelve el botón y le aplicamos el estilo
            # Esto es un truco común en Streamlit. Asegúrate de que el key sea único
            st.markdown(f"""
                <style>
                /* Target the div that contains the st.button with the specific key */
                [data-testid="stButton"][key="card_{modulo}"] > button {{
                    {clase_color}; /* Aplica todos los estilos de color y glassmorphism */
                    height: 150px; /* Asegura la altura */
                    border: none;
                }}
                [data-testid="stButton"][key="card_{modulo}"] > button:hover {{
                    transform: scale(1.05);
                    box-shadow: 0 6px 24px rgba(0,0,0,0.20);
                }}
                /* Para que el texto HTML interno se alinee y se muestre correctamente */
                [data-testid="stButton"][key="card_{modulo}"] > button div {{
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    padding: 0;
                    margin: 0;
                    width: 100%;
                }}
                </style>
            """, unsafe_allow_html=True)
            
    # ---------------------------------------
    # BOTÓN CERRAR SESIÓN
    # ---------------------------------------
    st.write("")  # Espaciado
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

# Fin del código corregido
