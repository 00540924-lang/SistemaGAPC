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
        margin-bottom: 18px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 4px 18px rgba(0,0,0,0.15);
        transition: 0.25s ease-in-out;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
        text-decoration: none;
        cursor: pointer;
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

    # ==========================================
    # TARJETAS CLICKEABLES QUE SÍ DISPARAN PYTHON
    # ==========================================
    for i, (icono, texto, modulo) in enumerate(modulos):
        clase_color = f"btn-glass btn{i+1}"

        with cols[i % 3]:

            # FORMULARIO HTML OCULTO (Streamlit SÍ lo procesa)
            st.markdown(
                f"""
                <form action="" method="post">
                    <input type="hidden" name="mod_seleccionado" value="{modulo}">
                    <button type="submit" style="all: unset; width:100%;">
                        <div class="{clase_color}">
                            <span class="icono-grande">{icono}</span>
                            {texto}
                        </div>
                    </button>
                </form>
                """,
                unsafe_allow_html=True
            )

    # ===== Leer POST del formulario =====
    if "mod_seleccionado" in st.session_state:
        mod = st.session_state["mod_seleccionado"]
        st.session_state["modulo_actual"] = mod
        st.rerun()

    # ===== Detectar acción POST =====
    import streamlit.web.server.websocket_headers as wh
    post_params = wh._get_websocket_headers().get("x-streamlit-post", "")

    if post_params:
        pairs = post_params.split("&")
        for p in pairs:
            if p.startswith("mod_seleccionado="):
                mod = p.replace("mod_seleccionado=", "")
                st.session_state["modulo_actual"] = mod
                st.rerun()

    # Botón cerrar sesión
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
