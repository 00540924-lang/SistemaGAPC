import streamlit as st

# -------------------------
# Funciones de cada módulo
# -------------------------
def mostrar_gestion_proyectos():
    st.write("📁 Contenido de Gestión de Proyectos")

def mostrar_inspecciones_evaluaciones():
    st.write("🧾 Contenido de Inspecciones y Evaluaciones")

def mostrar_gestion_documental():
    st.write("📄 Contenido de Gestión Documental")

def mostrar_reportes():
    st.write("📊 Contenido de Reportes")

def mostrar_configuracion():
    st.write("⚙️ Contenido de Configuración")

# -------------------------
# Función principal del menú
# -------------------------
def mostrar_menu():
    # Inicializar variable de sesión
    if "modulo" not in st.session_state:
        st.session_state["modulo"] = None

    # Título y mensaje
    st.markdown("""
        <h1 style='text-align:center; color:#4C3A60; font-size: 36px; margin-bottom:4px'>Menú Principal – GAPC</h1>
        <div style="background: linear-gradient(135deg, #B7A2C8, #F7C9A4); padding: 3px; border-radius: 12px; color: #4C3A60; font-size: 18px; text-align: center; width: 80%; box-shadow: 0px 4px 12px rgba(0,0,0,0.15); margin: auto;">
            <b>Seleccione un módulo para continuar</b><br>
        </div>
    """, unsafe_allow_html=True)

    # CSS para botones estilo tarjetas
    st.markdown("""
        <style>
        div.stButton > button {
            width: 150px; height: 150px; border-radius: 16px;
            color: white; font-weight: 700; font-size: 50px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
            cursor: pointer;
            margin: 10px;
            white-space: pre-line;  /* Permite saltos de línea en botón */
        }
        div.stButton > button:hover {
            transform: translateY(-8px) scale(1.03);
            box-shadow: 0 12px 30px rgba(0,0,0,0.20);
        }
        #btn_gestion_proyectos button { background: linear-gradient(135deg, #3085C3, #5BB3E6); }
        #btn_inspecciones button { background: linear-gradient(135deg, #FF9A56, #FEEAA1); color: #4C3A60; }
        #btn_gestion_documental button { background: linear-gradient(135deg, #1ABC9C, #7BE3C6); }
        #btn_reportes button { background: linear-gradient(135deg, #FF6B6B, #FFABAB); }
        #btn_configuracion button { background: linear-gradient(135deg, #9A86AE, #D6CDE2); color: #4C3A60; }
        </style>
    """, unsafe_allow_html=True)

    # Crear columnas para los botones
    cols = st.columns(5)
    with cols[0]:
        if st.button("📁\nGestión\nProyectos", key="btn_gestion_proyectos"):
            st.session_state["modulo"] = "gestion_proyectos"
    with cols[1]:
        if st.button("🧾\nInspecciones\ny Evaluaciones", key="btn_inspecciones"):
            st.session_state["modulo"] = "inspecciones_evaluaciones"
    with cols[2]:
        if st.button("📄\nGestión\nDocumental", key="btn_gestion_documental"):
            st.session_state["modulo"] = "gestion_documental"
    with cols[3]:
        if st.button("📊\nReportes", key="btn_reportes"):
            st.session_state["modulo"] = "reportes"
    with cols[4]:
        if st.button("⚙️\nConfiguración", key="btn_configuracion"):
            st.session_state["modulo"] = "configuracion"

    # Mostrar módulo seleccionado
    if st.session_state["modulo"]:
        st.markdown("---")
        st.subheader(f"🔎 Módulo seleccionado: {st.session_state['modulo'].replace('_',' ').capitalize()}")

        # Mostrar contenido del módulo
        if st.session_state["modulo"] == "gestion_proyectos":
            mostrar_gestion_proyectos()
        elif st.session_state["modulo"] == "inspecciones_evaluaciones":
            mostrar_inspecciones_evaluaciones()
        elif st.session_state["modulo"] == "gestion_documental":
            mostrar_gestion_documental()
        elif st.session_state["modulo"] == "reportes":
            mostrar_reportes()
        elif st.session_state["modulo"] == "configuracion":
            mostrar_configuracion()

    # Botón cerrar sesión centrado
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("🔒 Cerrar sesión", key="cerrar_sesion_btn"):
            st.session_state.clear()
            st.experimental_rerun()

# -------------------------
# Llamada principal
# -------------------------
if __name__ == "__main__":
    mostrar_menu()
