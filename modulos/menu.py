import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)
    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        st.stop()

    modulos = [
        ("📁", "Gestión de Proyectos", "proyectos"),
        ("👥", "Gestión de Usuarios", "registrar_miembros"),
        ("🧾", "Inspecciones y Evaluaciones", "inspecciones"),
        ("📄", "Gestión Documental", "documentos"),
        ("📊", "Reportes", "reportes"),
        ("⚙️", "Configuración", "configuracion"),
    ]

    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    st.markdown("""
    <style>
    .btn-glass {
        position: relative;
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
        overflow: hidden;
    }
    .btn-glass:hover {transform: scale(1.05); box-shadow: 0 6px 24px rgba(0,0,0,0.20);}
    .icono-grande {font-size: 42px; margin-bottom: 6px;}
    .btn1 { background: linear-gradient(135deg, #AEDFF7, #C9B2D9); }
    .btn2 { background: linear-gradient(135deg, #F7DCC4, #F4CDB3); }
    .btn3 { background: linear-gradient(135deg, #BEE4DD, #A6D9D0); }
    .btn4 { background: linear-gradient(135deg, #C9B2D9, #F7DCC4); }
    .btn5 { background: linear-gradient(135deg, #A6D9D0, #DCC8E3); }
    .btn6 { background: linear-gradient(135deg, #F4CDB3, #BEE4DD); }

    /* Botón invisible que cubre toda la tarjeta */
    .btn-invisible {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        opacity: 0;
        z-index: 2;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (icono, texto, modulo) in enumerate(modulos):
        clase_color = f"btn-glass btn{i+1}"
        with cols[i % 3]:
            # Botón de Streamlit invisible que hará la conexión
            boton_streamlit = st.button("", key=f"real_{modulo}")

            # Tarjeta HTML con botón invisible cubriendo toda la tarjeta
            st.markdown(f"""
            <div class="{clase_color}">
                <span class="icono-grande">{icono}</span>
                {texto}
                <button class="btn-invisible" onclick="document.querySelector('button[data-testid=stButton][key=real_{modulo}]').click()"></button>
            </div>
            """, unsafe_allow_html=True)

            # Acción al presionar
            if boton_streamlit:
                st.session_state.page = modulo
                st.rerun()

    # Botón cerrar sesión
    st.write("")
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
