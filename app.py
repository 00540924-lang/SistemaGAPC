import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu

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
    st.stop()  # ⛔ Detiene la ejecución

# ---- YA INICIÓ SESIÓN, MOSTRAR MENÚ ----
mostrar_menu()

# ---- CARGAR EL MÓDULO SEGÚN state ----
modulo = st.session_state.get("modulo")

# ---- Registrar Miembros ----
if modulo == "usuarios":
    # Importamos y ejecutamos tu módulo de registrar miembros
    from modulos.registrar_miembros import mostrar_registro_miembros
    mostrar_registro_miembros()

# ---- Otros módulos ----
elif modulo:
    # Suponiendo que tienes una función genérica para cargar otros módulos
    cargar_pagina(modulo)


