import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)
    # ... (código para definir 'modulos' sigue igual) ...

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

    # 🚨 CSS: Aseguramos la visibilidad de los botones de Streamlit para poder
    # manipularlos, pero el botón HTML será la interfaz visible.
    st.markdown("""
<style>
/* Estilos para el botón HTML visible (tarjeta) */
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

/* Nuevo CSS: Oculta el botón real de Streamlit que genera el "recuadro blanco" */
/* Lo hacemos invisible y lo posicionamos para que no interfiera visualmente */
.stButton > button {
    display: none; /* Oculta completamente el botón Streamlit nativo */
}

/* IMPORTANTE: Necesitamos un contenedor para nuestro botón HTML personalizado */
/* y asegurarnos que el HTML se muestre correctamente */
.custom-menu-card {
    position: relative;
    margin-bottom: 18px; /* Espacio para separar las filas */
}

</style>
""", unsafe_allow_html=True)

    # ---------------------------------------
    # GRID DE BOTONES
    # ---------------------------------------
    cols = st.columns(3)

    for i, (icono, texto, modulo) in enumerate(modulos):
        clase_color = f"btn-glass btn{i+1}"

        with cols[i % 3]:
            # 1. Botón Streamlit (invisible) que ejecuta la lógica
            # NOTA: Usamos un label vacío y no HTML
            boton_streamlit = st.button(" ", key=f"real_{modulo}") # Label simple

            # 2. Botón HTML (visible, la tarjeta)
            # Lo inyectamos antes del botón de Streamlit, o simplemente no importa el orden
            st.markdown(f"""
                <div class="custom-menu-card">
                    <button class="{clase_color}" id="btn_{modulo}">
                        <span class="icono-grande">{icono}</span>
                        {texto}
                    </button>
                </div>
                <script>
                // 3. JavaScript para conectar el clic de la tarjeta HTML al botón invisible de Streamlit
                const btnHtml = window.parent.document.getElementById("btn_{modulo}");
                
                // Buscamos el contenedor del botón Streamlit invisible. Esto varía según la versión.
                // Usaremos un selector más específico para que no interfiera con otros botones.
                const stBtnHidden = window.parent.document.querySelector('button[data-testid="stButton"][key="real_{modulo}"]');

                if (btnHtml) {{
                    btnHtml.addEventListener("click", function(){{
                        if (stBtnHidden) {{
                            stBtnHidden.click(); // Dispara el clic del botón Streamlit
                        }}
                    }});
                }}
                </script>
            """, unsafe_allow_html=True)

            # 4. Si se presionó el botón Streamlit invisible, cambiar la página
            if boton_streamlit:
                st.session_state.page = modulo
                st.rerun()

    # ---------------------------------------
    # BOTÓN CERRAR SESIÓN
    # ---------------------------------------
    st.write("")  # Espaciado
    # st.button() estándar (no necesita el truco HTML)
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
