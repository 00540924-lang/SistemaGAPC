import streamlit as st

def mostrar_menu():
    # Inicializar variable de sesión
    if "modulo" not in st.session_state:
        st.session_state["modulo"] = None

    # Obtener parámetros de la URL
    query_params = st.experimental_get_query_params()
    if "modulo" in query_params:
        st.session_state["modulo"] = query_params["modulo"][0]

    # Título
    st.markdown("""
        <h1 style='text-align:center; color:#4C3A60; font-size: 36px; margin-bottom:4px'>
            Menú Principal – GAPC
        </h1>
        """, unsafe_allow_html=True)

    # Tarjeta visual
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
            <b>Seleccione un módulo para continuar</b><br>
        </div>
        """, unsafe_allow_html=True)

    # CSS para tarjetas y botón
    st.markdown("""
        <style>
        .cards-row { display:flex; justify-content:center; gap:20px; flex-wrap:wrap; margin-top:15px; }
        .card {
            width:150px; height:150px; border-radius:16px; padding:18px;
            color:white; display:flex; flex-direction:column; justify-content:center; align-items:center;
            font-weight:700; font-size:50px; text-align:center; box-shadow:0 6px 18px rgba(0,0,0,0.12);
            transition: transform 0.18s ease, box-shadow 0.18s ease; cursor:pointer;
        }
        .g1 { background: linear-gradient(135deg, #3085C3, #5BB3E6); }
        .g2 { background: linear-gradient(135deg, #6A4BAF, #C08BE6); }
        .g3 { background: linear-gradient(135deg, #FF9A56, #FEEAA1); }
        .g4 { background: linear-gradient(135deg, #1ABC9C, #7BE3C6); }
        .g5 { background: linear-gradient(135deg, #FF6B6B, #FFABAB); }
        .g6 { background: linear-gradient(135deg, #9A86AE, #D6CDE2); }
        .card:hover { transform:translateY(-8px) scale(1.03); box-shadow:0 12px 30px rgba(0,0,0,0.20); }
        .card-sub { font-size:15px; font-weight:600; opacity:0.95; margin-top:0.2px; }

        /* Estilo del botón de cerrar sesión */
        div.stButton > button {
            background: linear-gradient(135deg, #B7A2C8, #F7C9A4);
            color: #4C3A60;
            border-radius: 12px;
            padding: 12px 24px;
            font-size: 18px;
            font-weight: 700;
            border: none;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
            margin-top: 70px;
        }
        div.stButton > button:hover {
            transform: translateY(-4px) scale(1.03);
            box-shadow: 0 12px 30px rgba(0,0,0,0.2);
        }
        </style>
        """, unsafe_allow_html=True)

    # Tarjetas visuales
    st.markdown("""
    <div class='cards-row'>
        <a href='?modulo=registrar_miembros'>
            <div class='card g2'>
                👥<div class='card-sub'>Registro de miembros</div>
            </div>
        </a>
        <a href='?modulo=inspecciones'>
            <div class='card g3'>
                🧾<div class='card-sub'>Inspecciones y Evaluaciones</div>
            </div>
        </a>
        <a href='?modulo=gestion_documental'>
            <div class='card g4'>
                📄<div class='card-sub'>Gestión Documental</div>
            </div>
        </a>
        <a href='?modulo=reportes'>
            <div class='card g5'>
                📊<div class='card-sub'>Reportes</div>
            </div>
        </a>
        <a href='?modulo=configuracion'>
            <div class='card g6'>
                ⚙️<div class='card-sub'>Configuración</div>
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Contenido del módulo
    if st.session_state["modulo"]:
        st.markdown("---")
        st.subheader(f"🔎 Módulo seleccionado: {st.session_state['modulo'].capitalize()}")
        st.write("Aquí aparecerá la interfaz y opciones específicas del módulo seleccionado.")

    # Botón de cerrar sesión centrado
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        if st.button("🔒 Cerrar sesión", key="cerrar_sesion_btn"):
            st.session_state.clear()
            st.experimental_rerun()  # Use rerun para reiniciar la app

# Ejecutar la función
if __name__ == "__main__":
    mostrar_menu()

