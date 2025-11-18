import streamlit as st
from streamlit_extras.stylable_container import stylable_container

def mostrar_menu():

    st.markdown("<h1 style='text-align:center; color:#4C3A60;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)
    st.write("")

    # --------- MODULOS -----------
    opciones = [
        {"id": "proyectos", "titulo": "Gestión de Proyectos", "icono": "📁"},
        {"id": "usuarios", "titulo": "Gestión de Usuarios", "icono": "👥"},
        {"id": "inspecciones", "titulo": "Inspecciones y Evaluaciones", "icono": "🧾"},
        {"id": "documentos", "titulo": "Gestión Documental", "icono": "📄"},
        {"id": "reportes", "titulo": "Reportes", "icono": "📊"},
        {"id": "configuracion", "titulo": "Configuración", "icono": "⚙️"},
    ]

    # 3 columnas
    cols = st.columns(3)

    for i, item in enumerate(opciones):
        col = cols[i % 3]

        with col:

            # TARJETA ESTÉTICA (Glassmorphism)
            with stylable_container(
                key=f"card_{item['id']}",
                css_styles=f"""
                    {{
                        background: linear-gradient(135deg, #ffffff99, #ffffff22);
                        padding: 22px;
                        border-radius: 20px;
                        cursor: pointer;
                        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
                        transition: 0.25s ease-in-out;
                        text-align:center;
                    }}
                    .styled-container:hover {{
                        transform: scale(1.05);
                        box-shadow: 0 6px 22px rgba(0,0,0,0.20);
                    }}
                """
            ):
                # CONTENIDO TARJETA
                st.markdown(
                    f"""
                    <div style="font-size:50px; margin-bottom:8px;">{item['icono']}</div>
                    <div style="font-size:18px; font-weight:700; color:#4C3A60;">
                        {item['titulo']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # ------------ CLICK INVISIBLE (NO MUESTRA NADA) ------------
                click_script = f"""
                    <script>
                        const card = window.parent.document.querySelector('[key="card_{item['id']}"]');
                        if (card) {{
                            card.onclick = () => {{
                                window.parent.postMessage({{"page": "{item['id']}"}}, "*");
                            }};
                        }}
                    </script>
                """
                st.markdown(click_script, unsafe_allow_html=True)

    # ------------ LISTENER GLOBAL PARA RECIBIR CLICK EN PYTHON ------------
    st.markdown("""
        <script>
            window.addEventListener("message", (event) => {
                if (event.data.page) {
                    const input = document.getElementById("streamlit-page-input");
                    input.value = event.data.page;
                    input.dispatchEvent(new Event("change"));
                }
            });
        </script>
    """, unsafe_allow_html=True)

    # INPUT OCULTO QUE STREAMLIT SI ESCUCHA
    st.text_input("", key="streamlit-page-input", label_visibility="hidden")

    # CAMBIO DE PÁGINA
    sel = st.session_state.get("streamlit-page-input", "")
    if sel:
        st.session_state["modulo_actual"] = sel
        st.rerun()

    # CERRAR SESIÓN
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
