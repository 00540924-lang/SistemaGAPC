from modulos.login import login
#from modulos.dashboard import dashboard
from modulos.menu import menu_principal
import streamlit as st

#if "usuario" not in st.session_state:
    #login()
#else:
    #dashboard()
# Estado inicial
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False
if "modulo" not in st.session_state:
    st.session_state["modulo"] = None

# Control de vistas
if st.session_state["sesion_iniciada"]:
    menu_principal()
else:
    login()
