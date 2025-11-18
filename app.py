import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu

# ==========================================
# CONFIGURACIÓN DE VARIABLES DE SESIÓN
# ==========================================
st.session_state.setdefault("sesion_iniciada", False)
st.session_state.setdefault("modulo_actual", "menu")  # Página por defecto del menú


# ==========================================
# LOGIN
# ==========================================
if not st.session_state["sesion_iniciada"]:
    login()
    st.stop()


# ==========================================
# DESPACHADOR DE PÁGINAS PRINCIPAL
# ==========================================
mod = st.session_state.get("modulo_actual", "menu")

# ---- MENÚ PRINCIPAL ----
if mod == "menu":
    mostrar_menu()

# ---- GESTIÓN DE PROYECTOS ----
elif mod == "proyectos":
    from modulos.proyectos import vista_proyectos
    vista_proyectos()

# ---- GESTIÓN DE USUARIOS ----
elif mod == "usuarios":
    from modulos.usuarios import vista_usuarios
    vista_usuarios()

# ---- INSPECCIONES ----
elif mod == "inspecciones":
    from modulos.inspecciones import vista_inspecciones
    vista_inspecciones()

# ---- DOCUMENTOS ----
elif mod == "documentos":
    from modulos.documentos import vista_documental
    vista_documental()

# ---- REPORTES ----
elif mod == "reportes":
    from modulos.reportes import vista_reportes
    vista_reportes()

# ---- CONFIGURACIÓN ----
elif mod == "configuracion":
    from modulos.configuracion import vista_configuracion
    vista_configuracion()

# ---- REGISTRAR MIEMBROS ----
elif mod == "registrar_miembros":
    from modulos.registrar_miembros import registrar_miembros
    registrar_miembros()

# ---- PÁGINA NO ENCONTRADA ----
else:
    st.error("❌ Página no encontrada.")
