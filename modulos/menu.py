import streamlit as st

def mostrar_menu():

    st.markdown(
        "<h1 style='text-align:center; color:#4C3A60;'>Menú Principal – GAPC</h1>",
        unsafe_allow_html=True
    )
    st.write("")

    # --------- MODULOS -----------
    opciones = [
        {"id": "proyectos", "titulo": "Gestión de Proyectos", "icono": "📁",
         "color": "linear-gradient(135deg, #B7D3F2, #C9B6E4)"},
        {"id": "usuarios", "titulo": "Gestión de Usuarios", "icono": "👥",
         "color": "linear-gradient(135deg, #F7D9C4, #E8B7DE)"},
        {"id": "inspecciones", "titulo": "Inspecciones y Evaluaciones", "icono": "🧾",
         "color": "linear-gradient(135deg, #A8E6CF, #DCEDC1)"},
        {"id": "documentos", "titulo": "Gestión Documental", "icono": "📄",
         "color": "linear-gradient(135deg, #EAD6EE, #F6EEC7)"},
        {"id": "reportes", "titulo": "Reportes", "icono": "📊",
         "color": "linear-gradient(135deg, #B2EBF2, #D7BDE2)"},
        {"id": "configuracion", "titulo": "Configuración", "icono": "⚙️",
         "color": "linear-gradient(135deg, #F7E7C4, #E3C4A8)"}
    ]

    cols = st.columns(3)

    for i, item in enumerate(opciones):
        col = cols[i % 3]
        with col:

            # TARJETA CON ESTILO Y CURSOR
            st.markdown(
                f"""
                <div class="card" id="card_{item['id']}"
                    style="
                        background:{item['color']};
                        padding: 30px;
                        border-radius: 22px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                        text-align:center;
                        cursor:pointer;
                        transition:0.2s;
                        margin-bottom: 25px;
                    ">
                    <div style="font-size:55px;">{item['icono']}</div>
                    <div style="margin-top:10px; font-size:19px; font-weight:700; color:#4C3A60;">
                        {item['titulo']}
                    </div>
                </div>

                <script>
                const card = window.parent.document.getElementById("card_{item['id']}");
                if (card) {{
                    card.onclick = () => {{
                        window.parent.postMessage({{"page": "{item['id']}"}}, "*");
                    }};
                }}
                </script>
                """,
                unsafe_allow_html=True
            )

    # LISTENER QUE STREAMLIT SÍ LEE
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

    st.text_input("", key="streamlit-page-input", label_visibility="hidden")

    sel = st.session_state.get("streamlit-page-input", "")
    if sel:
        st.session_state["page"] = sel
        st.rerun()

    # CERRAR SESIÓN
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
