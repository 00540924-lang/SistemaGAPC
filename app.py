import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu

# ==========================================
# CONFIGURACIÓN DE VARIABLES DE SESIÓN
# ==========================================
st.session_state.setdefault("sesion_iniciada", False)
st.session_state.setdefault("page", "menu")  # Página por defecto

# ==========================================
# LOGIN
# ==========================================
if not st.session_state["sesion_iniciada"]:
    login()
    st.stop()

# ==========================================
# DESPACHADOR DE PÁGINAS PRINCIPAL
# ==========================================
pagina = st.session_state.get("page", "menu")

# ---- MENÚ PRINCIPAL ----
if pagina == "menu":
    mostrar_menu()  # Aquí el botón "Credenciales" debe cambiar st.session_state["page"] = "credenciales"

# ---- GESTIÓN DE PROYECTOS ----
elif pagina == "proyectos":
    from modulos.proyectos import vista_proyectos
    vista_proyectos()

# ---- GESTIÓN DE USUARIOS (MIEMBROS) ----
elif pagina == "registrar_miembros":
    from modulos.registrar_miembros import registrar_miembros
    registrar_miembros()

# ---- GRUPOS ----
elif pagina == "grupos":
    from modulos.grupos import pagina_grupos
    pagina_grupos()

# ---- INSPECCIONES ----
elif pagina == "inspecciones":
    from modulos.inspecciones import vista_inspecciones
    vista_inspecciones()

# ---- DOCUMENTOS ----
elif pagina == "documentos":
    from modulos.documentos import vista_documental
    vista_documental()

# ---- REPORTES ----
elif pagina == "reportes":
    from modulos.reportes import vista_reportes
    vista_reportes()

# ---- CONFIGURACIÓN ----
elif pagina == "configuracion":
    from modulos.configuracion import vista_configuracion
    vista_configuracion()

# ---- CREDENCIALES ----
elif pagina == "credenciales":
    from modulos.credenciales import pagina_credenciales
    pagina_credenciales()

else:
    st.error("❌ Página no encontrada.")
