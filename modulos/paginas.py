import streamlit as st

def cargar_pagina(opcion):
    if opcion == "Gestión de Proyectos":
        pagina_proyectos()
    elif opcion == "Control de Personal":
        pagina_personal()
    elif opcion == "Inspecciones y Evaluaciones":
        pagina_inspecciones()
    elif opcion == "Gestión Documental":
        pagina_documentos()
    elif opcion == "Reportes":
        pagina_reportes()
    elif opcion == "Configuración":
        pagina_configuracion()
    else:
        st.write("Seleccione un módulo para continuar.")


# ----- PÁGINAS -----

def pagina_proyectos():
    st.title("📁 Gestión de Proyectos")
    st.write("Aquí irán las funciones para administrar proyectos.")


def pagina_personal():
    st.title("👥 Control de Personal")
    st.write("Aquí irán registros, asistencia, permisos, etc.")


def pagina_inspecciones():
    st.title("🧾 Inspecciones y Evaluaciones")
    st.write("Aquí se llenarán formularios y evaluaciones.")


def pagina_documentos():
    st.title("📄 Gestión Documental")
    st.write("Aquí podrás subir, clasificar y consultar documentos.")


def pagina_reportes():
    st.title("📊 Reportes")
    st.write("Aquí se generarán reportes en PDF/Excel y dashboards.")


def pagina_configuracion():
    st.title("⚙️ Configuración")
    st.write("Ajustes del sistema, usuarios, permisos, etc.")
