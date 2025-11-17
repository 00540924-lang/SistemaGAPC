import streamlit as st

def cargar_pagina(opcion):
    if opcion == "Inicio":
        pagina_inicio()
    elif opcion == "Usuarios":
        pagina_usuarios()
    elif opcion == "Inventario":
        pagina_inventario()
    elif opcion == "Reportes":
        pagina_reportes()
    else:
        st.error("Página no encontrada.")


def pagina_inicio():
    st.title("Inicio")
    st.write("Bienvenido al sistema.")


def pagina_usuarios():
    st.title("Gestión de Usuarios")
    st.write("Aquí puedes crear, editar y eliminar usuarios.")


def pagina_inventario():
    st.title("Inventario")
    st.write("Aquí se registran productos, entradas y salidas.")


def pagina_reportes():
    st.title("Reportes")
    st.write("Reportes generados por el sistema.")
