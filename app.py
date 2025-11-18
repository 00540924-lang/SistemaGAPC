import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu   # ✔️ IMPORT NECESARIO

# ------------------------------
# VARIABLES DE SESIÓN
# ------------------------------
st.session_state.setdefault("sesion_iniciada", False)
st.session_state.setdefault("page", "menu")

# ------------------------------
# LOGIN
# ------------------------------
if not st.session_state["sesion_iniciada"]:
    login()
    st.stop()

# ------------------------------
# ROUTER
# ------------------------------
page = st.session_state["page"]

if page == "menu":
    mostrar_menu()   # ✔️ Ahora sí funciona

elif page == "usuarios":
    from modulos.registrar_miembros import registrar_miembros
    registrar_miembros()

elif page == "proyectos":
    st.title("⚒ Gestión de Proyectos (Aún no implementado)")

elif page == "inspecciones":
    st.title("🔍 Inspecciones (Aún no implementado)")

elif page == "documentos":
    st.title("📄 Documentos (Aún no implementado)")

elif page == "reportes":
    st.title("📊 Reportes (Aún no implementado)")

elif page == "configuracion":
    st.title("⚙️ Configuración (Aún no implementado)")

else:
    st.error("❌ Página no encontrada.")
