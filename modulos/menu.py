import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)
    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # CSS para los botones según su key
    st.markdown("""
    <style>
    button[aria-label="btn_proyectos"] {
        background-color: #F4B400 !important;
        color: #4C3A60 !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
    }
    button[aria-label="btn_proyectos"]:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
    }

    button[aria-label="btn_registrar_miembros"] {
        background-color: #8E24AA !important;
        color: white !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
    }
    button[aria-label="btn_registrar_miembros"]:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
    }

    button[aria-label="btn_grupos"] {
        background-color: #E53935 !important;
        color: white !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
    }
    button[aria-label="btn_grupos"]:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
    }

    button[aria-label="btn_documentos"] {
        background-color: #1E88E5 !important;
        color: white !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
    }
    button[aria-label="btn_documentos"]:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
    }

    button[aria-label="btn_reportes"] {
        background-color: #43A047 !important;
        color: white !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
    }
    button[aria-label="btn_reportes"]:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
    }

    button[aria-label="btn_configuracion"] {
        background-color: #6D4C41 !important;
        color: white !important;
        width: 240px !important;
        height: 90px !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
    }
    button[aria-label="btn_configuracion"]:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
    }

    /* Logout */
    button[aria-label="logout_btn"] {
        width: 200px !important;
        height: 60px !important;
        background-color: #424242 !important;
        color: white !important;
        border-radius: 10px !important;
        transition: transform 0.2s ease !important;
    }
    button[aria-label="logout_btn"]:hover {
        transform: scale(1.05) !important;
        background-color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Título
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    modulos_base = [
        ("📁 Gestión de Proyectos", "proyectos", "btn_proyectos"),
        ("👥 Gestión de Usuarios", "registrar_miembros", "btn_registrar_miembros"),
        ("📝 Grupos", "grupos", "btn_grupos"),
        ("📄 Gestión Documental", "documentos", "btn_documentos"),
        ("📊 Reportes", "reportes", "btn_reportes"),
        ("⚙️ Configuración", "configuracion", "btn_configuracion"),
    ]

    rol = st.session_state.get("rol", None)

    if rol == "institucional":
        modulos = modulos_base

    elif rol == "promotor":
        modulos = [
            m for m in modulos_base if m[1] in ["proyectos", "grupos"]
        ]

    elif rol == "miembro":
        modulos = [
            m for m in modulos_base if m[1] == "documentos"
        ]

    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    cols = st.columns(3)
    for i, (texto, modulo, key) in enumerate(modulos):
        with cols[i % 3]:
            if st.button(texto, key=key):
                st.session_state.page = modulo
                st.experimental_rerun()

    st.write("---")
    if st.button("🔒 Cerrar sesión", key="logout_btn"):
        st.session_state.clear()
        st.experimental_rerun()

# Para probar la función (ejemplo):
if "rol" not in st.session_state:
    st.session_state["rol"] = "institucional"

mostrar_menu()
