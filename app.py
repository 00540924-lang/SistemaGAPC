import streamlit as st

# ==========================================
# CONFIGURACIÓN DE VARIABLES DE SESIÓN
# ==========================================
st.session_state.setdefault("sesion_iniciada", False)
st.session_state.setdefault("page", "menu")  # Página por defecto
st.session_state.setdefault("rol", None)
st.session_state.setdefault("id_grupo", None)

# ==========================================
# LOGIN
# ==========================================
if not st.session_state["sesion_iniciada"]:
    from modulos.login import login
    login()
    st.stop()

# ==========================================
# DESPACHADOR DE PÁGINAS
# ==========================================
pagina = st.session_state.get("page", "menu")

# ---- MENÚ PRINCIPAL ----
if pagina == "menu":
    from modulos.menu import mostrar_menu
    mostrar_menu()

# ---- PROYECTOS ----
elif pagina == "proyectos":
    from modulos.proyectos import vista_proyectos
    vista_proyectos()

# ---- REGISTRAR MIEMBROS ----
elif pagina == "registrar_miembros":
    from modulos.registrar_miembros import registrar_miembros
    registrar_miembros()

# ---- GRUPOS ----
elif pagina == "grupos":
    from modulos.grupos import pagina_grupos
    pagina_grupos()

# ---- INSPECCIONES ----
elif pagina == "inspecciones":
    from modulos.inspecciones import vista_inspecciones
    vista_inspecciones()

# ---- DOCUMENTOS ----
elif pagina == "documentos":
    from modulos.documentos import vista_documental
    vista_documental()

# ---- REPORTES ----
elif pagina == "reportes":
    from modulos.reportes import vista_reportes
    vista_reportes()

# ---- ASISTENCIA ----
elif pagina == "asistencia":
    from modulos.asistencia import mostrar_asistencia
    mostrar_asistencia()

# ---- CREDENCIALES ----
elif pagina == "credenciales":
    from modulos.credenciales import pagina_credenciales
    pagina_credenciales()

# ---- REGLAMENTO ----
elif pagina == "reglamento":
    from modulos.reglamento import mostrar_reglamento
    mostrar_reglamento()

# ---- MULTAS ----
elif pagina == "multas":
    from modulos.multas import multas_modulo
    multas_modulo()
# ---- PRESTAMOS ----
elif pagina == "prestamos":
    from modulos.prestamos import prestamos_modulo
    prestamos_modulo()

# ---- GAPC (solo rol Institucional) ----
elif pagina == "GAPC":
    from modulos.gapc import mostrar_gapc
    mostrar_gapc()

# ---- CAJA (SOLO MIEMBROS) ----
elif pagina == "caja":
    if st.session_state.get("rol") == "Miembro":
        from modulos.caja import mostrar_caja
        mostrar_caja()
    else:
        st.error("❌ No tiene permisos para acceder a este módulo.")

# ---- ERROR SI NO EXISTE ----
else:
    st.error("❌ Página no encontrada.")


