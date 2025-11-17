import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu
from modulos.paginas import cargar_pagina


# --- PARÁMETROS DE URL ---
query_params = st.experimental_get_query_params()
if "modulo" in query_params:
    st.session_state["modulo"] = query_params["modulo"][0]
else:
    st.session_state.setdefault("modulo", "menu")


# --- VARIABLES DE SESIÓN ---
st.session_state.setdefault("sesion_iniciada", False)
st.session_state.setdefault("modulo", "menu")


# -------------------- APLICACIÓN --------------------
if st.session_state["sesion_iniciada"]:

    # 🔹 Mostrar menú — devuelve la opción seleccionada
    opcion = mostrar_menu()

    # 🔹 Si seleccionó un módulo desde el menú
    if opcion:
        st.session_state["modulo"] = opcion

    # 🔹 Si el módulo es "registrar_miembros"
    if st.session_state["modulo"] == "registrar_miembros":
        from modulos.registrar_miembros import registrar_miembros
        registrar_miembros()

    # 🔹 Cargar otras páginas generales
    cargar_pagina(st.session_state["modulo"])

else:
    # ⏳ Mostrar login si no hay sesión
    login()
