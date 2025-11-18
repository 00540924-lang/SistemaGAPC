import streamlit as st

# ================================================================
#   SISTEMA DE NAVEGACIÓN ENTRE PANTALLAS
# ================================================================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "menu"

def ir(pagina):
    st.session_state["pagina"] = pagina
    st.experimental_set_query_params()
    st.rerun()


# ================================================================
#   MENÚ PRINCIPAL
# ================================================================
def mostrar_menu():

    rol = st.session_state.get("rol", "institucional")  # Para pruebas

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

    # ------------------------------------------------------------
    # TÍTULO
    # ------------------------------------------------------------
    st.markdown("""
        <h1 style='text-align:center; color:#4C3A60; font-size: 36px; margin-bottom:4px'>
            Menú Principal – GAPC
        </h1>
        """, unsafe_allow_html=True)

    # Tarjeta encabezado
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #B7A2C8, #F7C9A4);
            padding: 10px;
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

    # ------------------------------------------------------------
    # CSS COMPLETO (degradados + glass + iconos grandes)
    # ------------------------------------------------------------
    st.markdown("""
    <style>

    .btn-glass {
        padding: 18px;
        height: 150px;
        width: 100%;
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

    /* Icono más grande */
    .icono-grande {
        font-size: 45px;
        display: block;
        margin-bottom: 6px;
    }

    /* Degradados pastel inspirados en tu imagen */
    .btn1 { background: linear-gradient(135deg, #DCC8E3, #C9B2D9); }
    .btn2 { background: linear-gradient(135deg, #F7DCC4, #F4CDB3); }
    .btn3 { background: linear-gradient(135deg, #BEE4DD, #A6D9D0); }
    .btn4 { background: linear-gradient(135deg, #C9B2D9, #F7DCC4); }
    .btn5 { background: linear-gradient(135deg, #A6D9D0, #DCC8E3); }
    .btn6 { background: linear-gradient(135deg, #F4CDB3, #BEE4DD); }

    </style>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------------
    # TARJETAS DE LOS MÓDULOS
    # ------------------------------------------------------------
    cols = st.columns(3)

    for i, (icono, texto, modulo) in enumerate(modulos):
        clase_color = f"btn-glass btn{i+1}"
        with cols[i % 3]:
            st.markdown(
                f"""
                <button class="{clase_color}" onclick="window.location.href='/?go={modulo}'">
                    <span class="icono-grande">{icono}</span>
                    {texto}
                </button>
                """,
                unsafe_allow_html=True
            )

    # Detectar navegación
    query = st.experimental_get_query_params()
    if "go" in query:
        ir(query["go"][0])

    # Botón cerrar sesión
    st.write("")
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("🔒 Cerrar sesión"):
            st.session_state.clear()
            st.rerun()


# ================================================================
#   PÁGINA: GESTIÓN DE USUARIOS
# ================================================================
def pagina_usuarios():
    st.title("Gestión de Usuarios")

    opcion = st.radio(
        "Seleccione una acción",
        ["➕ Añadir Usuario", "🗑️ Eliminar Usuario"]
    )

    if opcion == "➕ Añadir Usuario":
        st.subheader("Añadir Usuario")
        nombre = st.text_input("Nombre completo")
        correo = st.text_input("Correo electrónico")
        rol = st.selectbox("Rol", ["Institucional", "Promotor", "Miembro"])

        if st.button("Guardar Usuario"):
            st.success(f"Usuario '{nombre}' registrado correctamente.")

    elif opcion == "🗑️ Eliminar Usuario":
        st.subheader("Eliminar Usuario")
        usuario = st.selectbox("Seleccione un usuario", ["Luis", "Ana", "Carlos"])

        if st.button("Eliminar"):
            st.warning(f"Usuario '{usuario}' eliminado.")

    st.write("")
    if st.button("⤶ Volver al menú"):
        ir("menu")


# ================================================================
#   CONTROLADOR PRINCIPAL (decide qué pantalla mostrar)
# ================================================================
if st.session_state["pagina"] == "menu":
    mostrar_menu()

elif st.session_state["pagina"] == "usuarios":
    pagina_usuarios()

# Aquí puedes agregar más módulos:
# elif st.session_state["pagina"] == "proyectos":
#     pagina_proyectos()

