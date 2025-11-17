import streamlit as st

def mostrar_menu():
    # inicializar variable de sesión si no existe
    if "modulo" not in st.session_state:
        st.session_state["modulo"] = None

    # Título
    st.markdown(
        """
        <h1 style='text-align:center; color:#3085C3; margin-bottom:4px'>
            Panel Principal – GAPC
        </h1>
        <p style='text-align:center; color:#556; margin-top:0;'>
            Seleccione un módulo para continuar
        </p>
        """,
        unsafe_allow_html=True,
    )

    # CSS de las tarjetas y botones (PRO look)
    st.markdown(
        """
        <style>
        .cards-row {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 25px;
        }

        .card {
            width: 280px;
            height: 150px;
            border-radius: 16px;
            padding: 18px;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-weight: 700;
            font-size: 20px;
            text-align: center;
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
            cursor: pointer;
        }

        /* Gradiente base */
        .g1 { background: linear-gradient(135deg, #3085C3, #5BB3E6); }
        .g2 { background: linear-gradient(135deg, #6A4BAF, #C08BE6); }
        .g3 { background: linear-gradient(135deg, #FF9A56, #FEEAA1); }
        .g4 { background: linear-gradient(135deg, #1ABC9C, #7BE3C6); }
        .g5 { background: linear-gradient(135deg, #FF6B6B, #FFABAB); }
        .g6 { background: linear-gradient(135deg, #9A86AE, #D6CDE2); }

        .card:hover {
            transform: translateY(-8px) scale(1.03);
            box-shadow: 0 12px 30px rgba(0,0,0,0.20);
        }

        /* Estilo para los botones nativos de Streamlit para que ocupen todo el espacio de la tarjeta */
        .stButton>button {
            height: 150px;
            width: 280px;
            padding: 0;
            border-radius: 16px;
            background: transparent;
            border: none;
            font-weight: 700;
            font-size: 20px;
        }

        /* Texto secundario debajo del título (pequeño) */
        .card-sub {
            font-size: 13px;
            font-weight: 600;
            opacity: 0.95;
            margin-top: 6px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # Botones (usamos layout de columnas para que queden alineados)
    # Cada st.button está visualmente alineado con la tarjeta HTML que mostramos luego.
    cols = st.columns([1,1,1])
    with cols[0]:
        if st.button("📁 Gestión de Proyectos", key="proyectos"):
            st.session_state["modulo"] = "proyectos"
            st.rerun()
    with cols[1]:
        if st.button("👥 Control de Personal", key="personal"):
            st.session_state["modulo"] = "personal"
            st.rerun()
    with cols[2]:
        if st.button("🧾 Inspecciones", key="inspecciones"):
            st.session_state["modulo"] = "inspecciones"
            st.rerun()

    st.write("")  # separador

    cols2 = st.columns([1,1,1])
    with cols2[0]:
        if st.button("📄 Gestión Documental", key="documentos"):
            st.session_state["modulo"] = "documentos"
            st.rerun()
    with cols2[1]:
        if st.button("📊 Reportes", key="reportes"):
            st.session_state["modulo"] = "reportes"
            st.rerun()
    with cols2[2]:
        if st.button("⚙️ Configuración", key="configuracion"):
            st.session_state["modulo"] = "configuracion"
            st.rerun()

    # Visual: tarjetas decorativas (no clicables, sirven como "mockup" visual)
    st.markdown(
        """
        <div class='cards-row'>
            <div class='card g1'>📁<div class='card-sub'>Gestión de Proyectos</div></div>
            <div class='card g2'>👥<div class='card-sub'>Control de Personal</div></div>
            <div class='card g3'>🧾<div class='card-sub'>Inspecciones y Evaluaciones</div></div>
            <div class='card g4'>📄<div class='card-sub'>Gestión Documental</div></div>
            <div class='card g5'>📊<div class='card-sub'>Reportes</div></div>
            <div class='card g6'>⚙️<div class='card-sub'>Configuración</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Muestra un resumen del módulo seleccionado
    if st.session_state["modulo"]:
        st.markdown("---")
        st.subheader(f"🔎 Módulo seleccionado: {st.session_state['modulo'].capitalize()}")
        st.write("Aquí aparecerá la interfaz y opciones específicas del módulo seleccionado.")
