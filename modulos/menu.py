import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        # Quitamos st.stop() temporalmente para ver si el error se propaga
        # st.stop() 
        return

    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)
    
    # Inicializar módulos para evitar NameError
    modulos = []
    
    # Definición simplificada para prueba: (Texto, Modulo Key)
    modulos_base = [
        ("Gestión de Proyectos", "proyectos"),
        ("Gestión de Usuarios", "registrar_miembros"),
        ("Inspecciones y Evaluaciones", "inspecciones"),
        ("Gestión Documental", "documentos"),
        ("Reportes", "reportes"),
        ("Configuración", "configuracion"),
    ]
    
    # Lógica de asignación de módulos (simplificada para la prueba)
    if rol == "institucional":
        modulos = modulos_base
    elif rol == "promotor":
        modulos = [m for m in modulos_base if m[1] in ["proyectos", "inspecciones"]]
    elif rol == "miembro":
        modulos = [m for m in modulos_base if m[1] in ["documentos"]]

    if not modulos:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # Usamos botones Streamlit estándar sin CSS complejo
    cols = st.columns(3)
    
    for i, (texto, modulo) in enumerate(modulos):
        with cols[i % 3]:
            if st.button(
                label=texto, 
                key=f"simple_{modulo}"
            ):
                st.session_state.page = modulo
                st.rerun()

    st.write("---")
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
