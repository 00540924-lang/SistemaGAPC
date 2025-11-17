import streamlit as st

def mostrar_menu():
    # inicializar variable de sesión si no existe
    if "modulo" not in st.session_state:
        st.session_state["modulo"] = None

    # Título
    st.markdown(
        """
        <h1 style='text-align:center; color:#4C3A60; font-size: 36px; margin-bottom:4px'>
            Menú Principal – GAPC
        </h1>
        """,
        unsafe_allow_html=True,
    )

    # -------- TARJETA VISUAL ----------
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #B7A2C8, #F7C9A4);
            padding: 3px;
            border-radius: 12px;
            color: #ffffff;
            font-size: 18px;
            text-align: center;
            width: 80%;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
            margin: auto;
        ">
            <b>Seleccione un módulo para continuar</b><br>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------- CSS TARJETAS --------
    st.markdown(
        """
        <style>
        .cards-row {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 15px;
        }

        .card {
            width: 150px;
            height: 150px;
            border-radius: 16px;
            padding: 18px;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-weight: 700;
            font-size: 50px;
            text-align: center;
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
            cursor: pointer;
        }

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

        .card-sub {
            font-size: 15px;
            font-weight: 600;
            opacity: 0.95;
            margin-top: 0.2px;
        }

        /* BOTÓN DE CERRAR SESIÓN */
        .logout-btn {
            background: linear-gradient(135deg, #B7A2C8, #F7C9A4);
            padding: 12px 24px;
            color: #B7A2C8, #F7C9A4 !important;
            font-weight: bold;
            font-size: 18px;
            border-radius: 12px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            margin-top: 40px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            transition: 0.2s;
        }
        .logout-btn:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 18px rgba(0,0,0,0.25);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # -------- TARJETAS VISUALES --------
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

    # -------- CONTENIDO DEL MÓDULO --------
    if st.session_state["modulo"]:
        st.markdown("---")
        st.subheader(f"🔎 Módulo seleccionado: {st.session_state['modulo'].capitalize()}")
        st.write("Aquí aparecerá la interfaz y opciones específicas del módulo seleccionado.")

# -------- BOTÓN CERRAR SESIÓN CON GRADIENTE --------

# Espacio antes del botón
st.markdown("<br><br><br>", unsafe_allow_html=True)

# CSS para el botón con gradiente
st.markdown("""
    <style>
    /* Botón con gradiente */
    div.stButton > button {
        background: linear-gradient(135deg, #B7A2C8, #F7C9A4); /* Gradiente */
        color: #4C3A60;            /* Color del texto */
        border-radius: 12px;       /* Bordes redondeados */
        padding: 12px 24px;        /* Tamaño */
        font-size: 16px;           /* Tamaño texto */
        font-weight: 700;          /* Negrita */
        border: none;              /* Sin borde */
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }

    /* Hover del botón */
    div.stButton > button:hover {
        transform: translateY(-4px) scale(1.03);
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Botón centrado
col1, col2, col3 = st.columns([1,3,1])
with col2:
    if st.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

