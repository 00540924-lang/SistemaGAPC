import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu

# -------------------------
# VARIABLES DE SESIÓN
# -------------------------
st.session_state.setdefault("sesion_iniciada", False)
st.session_state.setdefault("page", "menu")  # Página inicial por defecto


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

# ---- GESTIÓN USUARIOS ----
elif pagina == "gestion_usuarios":
    from modulos.gestion_usuarios import gestion_usuarios
    gestion_usuarios()

# ---- CUALQUIER OTRO MÓDULO ----
# Puedes agregar más formularios aquí:
# elif pagina == "inventario":
#     from modulos.inventario import inventario
#     inventario()


