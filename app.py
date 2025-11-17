import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu
from modulos.paginas import cargar_pagina   # ← IMPORTANTE


# ----- CONTROL DE SESIÓN -----
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if "modulo" not in st.session_state: 
    st.session_state["modulo"] = None


# ----- APP -----
if st.session_state["sesion_iniciada"]:
    st.set_page_config(page_title="Sistema GAPC", layout="wide")
    # Mostrar menú y capturar el módulo seleccionado
    opcion = mostrar_menu()

    # Cargar la página correspondiente
    if opcion:
        cargar_pagina(opcion)

else:
    login()


