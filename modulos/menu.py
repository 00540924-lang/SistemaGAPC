import streamlit as st
import time # Importamos 'time' por si necesitamos un pequeño retardo (opcional)

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        st.stop()

    # ---------------------------------------
    # CONFIGURAR MÓDULOS SEGÚN ROL (código omitido, asumiendo que es correcto)
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
    # TÍTULO Y CSS (código omitido, asumiendo que es correcto)
    # ---------------------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # ... (Bloque <style> CSS, debe estar completo y ocultar .stButton > button) ...

    st.markdown("""
<style>
/* ... (Todo tu CSS de .btn-glass y ocultar .stButton > button) ... */
.stButton > button {
    display: none !important; 
}
/* ... */
</style>
""", unsafe_allow_html=True)
    
    # ---------------------------------------
    # GRID DE BOTONES Y GENERACIÓN DE HTML
    # ---------------------------------------
    cols = st.columns(3)
    
    js_final_script = "<script>"

    for i, (icono, texto, modulo) in enumerate(modulos):
        clase_color = f"btn-glass btn{i+1}"

        with cols[i % 3]:
            # 1. Botón Streamlit (invisible) que ejecuta la lógica
            # Es VITAL para la funcionalidad.
            boton_streamlit = st.button(" ", key=f"real_{modulo}")

            # 2. Botón HTML (visible, la tarjeta)
            st.markdown(f"""
                <div class="custom-menu-card">
                    <button class="{clase_color}" id="btn_{modulo}">
                        <span class="icono-grande">{icono}</span>
                        {texto}
                    </button>
                </div>
            """, unsafe_allow_html=True)

            # 3. Código JavaScript con selector más robusto
            # Buscamos el contenedor padre (data-testid="stButton") que contiene el key.
            # Luego, buscamos el botón <button> dentro de ese contenedor.
            js_final_script += f"""
                const btnHtml_{modulo} = window.parent.document.getElementById("btn_{modulo}");
                
                // 🚨 Selector más robusto: Busca el contenedor stButton que contiene el key.
                const stBtnContainer = window.parent.document.querySelector('[data-testid="stButton"] button[key="real_{modulo}"]').closest('[data-testid="stButton"]');
                
                if (btnHtml_{modulo} && stBtnContainer) {{
                    // Luego, buscamos el botón real dentro de ese contenedor.
                    const stBtnHidden_{modulo} = stBtnContainer.querySelector('button');
                    
                    if (stBtnHidden_{modulo}) {{
                        // Si ambos existen, adjuntamos el evento de clic
                        btnHtml_{modulo}.addEventListener("click", () => {{
                            stBtnHidden_{modulo}.click(); 
                        }});
                    }}
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
    # Inyectamos el script completo DESPUÉS de todas las columnas.
    st.markdown(js_final_script, unsafe_allow_html=True)
    
    # ---------------------------------------
    # BOTÓN CERRAR SESIÓN
    # ---------------------------------------
    st.write("") 
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
