import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu

# -------------------------
# VARIABLES DE SESIÓN
# -------------------------
st.session_state.setdefault("sesion_iniciada", False)
st.session_state.setdefault("page", "menu")  # Página por defecto


# -------------------------
# LOGIN
# -------------------------
if not st.session_state["sesion_iniciada"]:
    login()
    st.stop()


# -------------------------
# DESPACHADOR DE PÁGINAS
# -------------------------
pagina = st.session_state.get("page", "menu")

# ---- MENÚ PRINCIPAL ----
if pagina == "menu":
    mostrar_menu()

# ---- REGISTRAR MIEMBROS ----
elif pagina == "registrar_miembros":
    from modulos.registrar_miembros import registrar_miembros
    registrar_miembros()

# ---- AGREGAR AQUÍ TUS OTROS MÓDULOS ----
elif pagina == "proyectos":
    from modulos.proyectos import proyectos
    proyectos()

elif pagina == "usuarios":
    from modulos.usuarios import usuarios
    usuarios()

elif pagina == "inspecciones":
    from modulos.inspecciones import inspecciones
    inspecciones()

elif pagina == "documentos":
    from modulos.documentos import documentos
    documentos()

elif pagina == "reportes":
    from modulos.reportes import reportes
    reportes()

elif pagina == "configuracion":
    from modulos.configuracion import configuracion
    configuracion()
