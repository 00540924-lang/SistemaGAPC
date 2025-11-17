import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu

if "logged" not in st.session_state:
    st.session_state["logged"] = False

if st.session_state["logged"]:
    mostrar_menu()
else:
    login()

