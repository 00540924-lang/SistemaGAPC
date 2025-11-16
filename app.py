# app.py
import streamlit as st
from modulos.login import login

# Comprobamos si la sesión ya está iniciada
if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
else:
# Si la sesión no está iniciada, mostrar el login
login()
