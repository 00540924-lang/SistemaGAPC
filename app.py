import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu
from modulos.paginas import cargar_pagina

# ---- LEER PARÁMETROS DE URL ----
query_params = st.experimental_get_query_params()
if "modulo" in query_params:
    st.session_state["modulo"] = query_params["modulo"][0]
else:
    st.session_state.setdefault("modulo", None)

# ---- VARIABLES DE SESIÓN ----
st.session_state.setdefault("sesion_iniciada", False)

# ---- SI NO HA INICIADO SESIÓN, MOSTRAR LOGIN ----
if not st.session_state["sesion_iniciada"]:
    login()
    st.stop()   # ⛔ Detiene la ejecución aquí
                # evita que se “regrese” al login

# ---- YA INICIÓ SESIÓN, MOSTRAR MENÚ ----
opcion = mostrar_menu()

# ---- CARGAR EL MÓDULO SELECCIONADO ----
if opcion == "registrar_miembros":
    from modulos.registrar_miembros import registrar_miembros
    registrar_miembros()

elif opcion:
    cargar_pagina(opcion)
