import streamlit as st

def mostrar_menu():

    rol = st.session_state.get("rol", None)
    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        st.stop()

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

    st.markdown("<h1 style='text-align:center; color:#4C3A60;'>Menú Principal – GAPC</h1>",
                unsafe_allow_html=True)

    # ===== CSS =====
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
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 4px 18px rgba(0,0,0,0.15);
        transition: 0.25s ease-in-out;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
        cursor: pointer;
        margin-bottom: 18px;
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

    cols = st.columns(3)

    # ======================================
    # TARJETAS STREAMLIT 100% FUNCIONALES
    # ======================================
    for i, (icono, texto, modulo) in enumerate(modulos):

        clase = f"btn-glass btn{i+1}"
        btn_id = f"btn_{modulo}"

        with cols[i % 3]:

            # Botón invisible
            clicked = st.button(" ", key=btn_id, label_visibility="collapsed")

            if clicked:
                st.session_state["page"] = modulo
                st.rerun()

            # Tarjeta HTML que activa el botón invisible
            st.markdown(
                f"""
                <div class="{clase}" onclick="document.getElementById('{btn_id}').click();">
                    <span class="icono-grande">{icono}</span>
                    <p>{texto}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # BOTÓN CERRAR SESIÓN
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
