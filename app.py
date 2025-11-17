import streamlit as st
from modulos.login import login
from modulos.menu import menu_principal

if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if st.session_state["sesion_iniciada"]:
    mostrar_menu()
else:
    login()
