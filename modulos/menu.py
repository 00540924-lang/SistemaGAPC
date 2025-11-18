import streamlit as st

def mostrar_menu():

    # ---------------------------------------
    # LEER ROL DEL USUARIO DESDE EL LOGIN
    # ---------------------------------------
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

    else:
        st.error("❌ Rol no reconocido.")
        st.stop()

    # ---------------------------------------
    # TÍTULO
    # ---------------------------------------
    st.markdown("""
        <h1 style='text-align:center; color:#4C3A60; font-size: 36px; margin-bottom:4px'>
            Menú Principal – GAPC
        </h1>
        """, unsafe_allow_html=True)

    # Tarjeta encabezado
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #B7A2C8, #F7C9A4);
            padding: 3px;
            border-radius: 12px;
            color: #4C3A60;
            font-size: 18px;
            text-align: center;
            width: 80%;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
            margin: auto;
        ">
            <b>Seleccione un módulo para continuar</b>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------
    # CSS GLASSMORPHISM + COLORES DIFERENTES
    # ---------------------------------------
    st.markdown("""
<style>
.btn-glass {
    padding: 18px;
    height: 150px;
    width: 400;
    border-radius: 18px;
    color: #4C3A60;
    font-size: 18px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    margin-bottom: 18px;

    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 4px 18px rgba(0,0,0,0.15);
    transition: 0.25s ease-in-out;
}

.btn-glass:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 24px rgba(0,0,0,0.20);
}

/* Degradados individuales */
<style>
/* Paleta basada en tu imagen GAPC */

.btn1 { 
    background: linear-gradient(135deg, #DCC8E3, #C9B2D9); 
}  /* Lila pastel */
.btn2 { 
    background: linear-gradient(135deg, #F7DCC4, #F4CDB3); 
}  /* Durazno pastel */
.btn3 { 
    background: linear-gradient(135deg, #BEE4DD, #A6D9D0); 
}  /* Verde/Aqua pastel */
.btn4 { 
    background: linear-gradient(135deg, #C9B2D9, #F7DCC4); 
}  /* Lila → Durazno */
.btn5 { 
    background: linear-gradient(135deg, #A6D9D0, #DCC8E3); 
}  /* Aqua → Lavanda */
.btn6 { 
    background: linear-gradient(135deg, #F4CDB3, #BEE4DD); 
}  /* Melocotón → Menta */
</style>
""", unsafe_allow_html=True)

    # ---------------------------------------
    # TARJETAS POR MÓDULOS
    # ---------------------------------------
    st.write("")
    cols = st.columns(3)

    for i, (icono, texto, modulo) in enumerate(modulos):
        clase_color = f"btn-glass btn{i+1}"  # btn1, btn2...
        with cols[i % 3]:
            clicked = st.markdown(
                f"""
                <button class="{clase_color}" onclick="window.location.href='/?mod={modulo}'">
                    {icono}<br>{texto}
                </button>
                """,
                unsafe_allow_html=True
            )
            if f"btn_{modulo}" in st.session_state:
                st.session_state["modulo"] = modulo
                st.rerun()

    # ---------------------------------------
    # BOTÓN CERRAR SESIÓN
    # ---------------------------------------
    st.write("")
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("🔒 Cerrar sesión", key="cerrar_sesion_btn"):
            st.session_state.clear()
            st.rerun()

        if st.button("🔒 Cerrar sesión", key="cerrar_sesion_btn"):
            st.session_state.clear()
            st.rerun()
