import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu  # si tienes un menú separado

def main():
    if "sesion_iniciada" not in st.session_state:
        st.session_state["sesion_iniciada"] = False

    if st.session_state["sesion_iniciada"]:
        mostrar_menu()   # <- Lo que viene después del login
    else:
        login()

if __name__ == "__main__":
    main()

