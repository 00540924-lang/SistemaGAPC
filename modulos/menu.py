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
            ("👥", "Gestión de Usuarios", "usuarios"),
            ("🧾", "Inspecciones y Evaluaciones", "inspecciones"),
            ("📄", "Gestión Documental", "documentos"),
            ("📊", "Reportes", "reportes"),
            ("⚙️", "Configuración", "configuracion"),
            ("➕", "Registrar Miembros", "registrar_miembros"),
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

    st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

    # ---------------------------------------
    # GRID DE BOTONES
    # ---------------------------------------
    cols = st.columns(3)

    for i, (icono, texto, modulo) in enumerate(modulos):
        clase_color = f"btn-glass btn{i+1}"

        with cols[i % 3]:
            # --- BOTÓN STREAMLIT REAL ---
            if st.button(f"{icono} {texto}", key=f"btn_{modulo}"):
                st.session_state.page = modulo
                st.rerun()

    # ---------------------------------------
    # BOTÓN CERRAR SESIÓN
    # ---------------------------------------
    st.write("")  # espaciado
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
