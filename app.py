import streamlit as st
from modulos.login import login   # tu login real
from modulos.menu import mostrar_menu

# ------------------------------
# VARIABLES DE SESIÓN INICIALES
# ------------------------------
st.session_state.setdefault("sesion_iniciada", False)
st.session_state.setdefault("rol", None)
st.session_state.setdefault("modulo", None)

# ------------------------------
# LEER PARÁMETROS DE URL
# ------------------------------
query_params = st.experimental_get_query_params()
if "modulo" in query_params:
    st.session_state["modulo"] = query_params["modulo"][0]

# ------------------------------
# MOSTRAR LOGIN SI NO HA INICIADO SESIÓN
# ------------------------------
if not st.session_state["sesion_iniciada"]:
    login()       # <--- tu login real
    st.stop()     # ⛔ Detiene la ejecución hasta que se inicie sesión

# ------------------------------
# YA INICIÓ SESIÓN, MOSTRAR MENÚ
# ------------------------------
mostrar_menu()

# ------------------------------
# CARGAR EL MÓDULO SEGÚN STATE
# ------------------------------
modulo = st.session_state.get("modulo")

if modulo == "registrar_miembros":
    from modulos.registrar_miembros import registrar_miembros
    registrar_miembros()

elif modulo:
    # Suponiendo que tienes una función genérica para cargar módulos
    try:
        from modulos.cargar_pagina import cargar_pagina
        cargar_pagina(modulo)
    except ImportError:
        st.error(f"❌ No se pudo cargar el módulo: {modulo}")
