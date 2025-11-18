import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        st.stop()

    # ---------------------------------------
    # CONFIGURAR MÓDULOS SEGÚN ROL (Mantenemos la definición de modulos)
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

    # El CSS sigue igual. Asegúrate de que este bloque esté completo y al inicio.
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

/* Oculta el botón real de Streamlit que genera el "recuadro blanco" */
.stButton > button {
    display: none !important; /* Usamos !important para asegurar que se oculte */
}

.custom-menu-card {
    /* Mantenemos el contenedor si es necesario para el layout, pero no para la lógica JS */
    position: relative;
    margin-bottom: 18px; 
}
</style>
""", unsafe_allow_html=True)

    # ---------------------------------------
    # GRID DE BOTONES Y GENERACIÓN DE HTML
    # ---------------------------------------
    cols = st.columns(3)
    
    # 🚨 String para almacenar todo el JS que se inyectará al final
    js_final_script = "<script>"

    for i, (icono, texto, modulo) in enumerate(modulos):
        clase_color = f"btn-glass btn{i+1}"

        with cols[i % 3]:
            # 1. Botón Streamlit (invisible) que ejecuta la lógica
            # Es vital que exista para que Streamlit detecte el clic.
            boton_streamlit = st.button(" ", key=f"real_{modulo}")

            # 2. Botón HTML (visible, la tarjeta)
            # Solo inyectamos el HTML de la tarjeta, sin el script.
            st.markdown(f"""
                <div class="custom-menu-card">
                    <button class="{clase_color}" id="btn_{modulo}">
                        <span class="icono-grande">{icono}</span>
                        {texto}
                    </button>
                </div>
            """, unsafe_allow_html=True)

            # 3. Añadimos el código JavaScript necesario para este botón a la cadena js_final_script
            # El JS ahora es una sola línea por botón para ser más robusto.
            js_final_script += f"""
                const btnHtml_{modulo} = window.parent.document.getElementById("btn_{modulo}");
                const stBtnHidden_{modulo} = window.parent.document.querySelector('button[data-testid="stButton"][key="real_{modulo}"]');
                if (btnHtml_{modulo} && stBtnHidden_{modulo}) {{
                    btnHtml_{modulo}.addEventListener("click", () => stBtnHidden_{modulo}.click());
                }}
            """

            # 4. Si se presionó el botón Streamlit invisible, cambiar la página
            if boton_streamlit:
                st.session_state.page = modulo
                st.rerun()

    # ---------------------------------------
    # INYECCIÓN FINAL DE JAVASCRIPT
    # ---------------------------------------
    js_final_script += "</script>"
    # 🚨 Inyectamos el script completo fuera de las columnas
    st.markdown(js_final_script, unsafe_allow_html=True)

    # ---------------------------------------
    # BOTÓN CERRAR SESIÓN
    # ---------------------------------------
    st.write("") 
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
