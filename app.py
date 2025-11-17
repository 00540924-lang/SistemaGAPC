import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu
from modulos.paginas import cargar_pagina   # ← IMPORTANTE

# --- LEER PARÁMETROS DE LA URL ---
query_params = st.experimental_get_query_params()

if "modulo" in query_params:
    st.session_state["modulo"] = query_params["modulo"][0]
else:
    st.session_state.setdefault("modulo", "menu")


# ----- CONTROL DE SESIÓN -----
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if "modulo" not in st.session_state: 
    st.session_state["modulo"] = None


# ----- APP -----
if st.session_state["sesion_iniciada"]:
    # Mostrar menú y capturar el módulo seleccionado
    opcion = mostrar_menu()

    # Cargar la página correspondiente
    if opcion:
        cargar_pagina(opcion)

else:
    login()


