import streamlit as st
from modulos.login import login

# Inicializar variable si no existe
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

# Si la sesión está iniciada
if st.session_state["sesion_iniciada"]:
    st.title("Bienvenido al sistema")
    st.write("Contenido interno del sistema aquí...")

# Si NO está iniciada
else:
    login()

