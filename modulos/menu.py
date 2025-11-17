import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu
from modulos.paginas.proyectos import pagina_proyectos
from modulos.paginas.personal import pagina_personal
from modulos.paginas.inspecciones import pagina_inspecciones
from modulos.paginas.documentos import pagina_documentos
from modulos.paginas.reportes import pagina_reportes
from modulos.paginas.configuracion import pagina_configuracion


# Inicializar sesión
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if "pagina_actual" not in st.session_state:
    st.session_state["pagina_actual"] = None


# ------------------------------------------------------
#                LÓGICA PRINCIPAL DE LA APP
# ------------------------------------------------------
if st.session_state["sesion_iniciada"]:

    # Si no se ha seleccionado una página → mostrar menú
    if st.session_state["pagina_actual"] is None:
        opcion = mostrar_menu()

    else:
        # Abrir la página correspondiente
        pagina = st.session_state["pagina_actual"]

        if pagina == "proyectos":
            pagina_proyectos()

        elif pagina == "personal":
            pagina_personal()

        elif pagina == "inspecciones":
            pagina_inspecciones()

        elif pagina == "documentos":
            pagina_documentos()

        elif pagina == "reportes":
            pagina_reportes()

        elif pagina == "configuracion":
            pagina_configuracion()

else:
    login()

