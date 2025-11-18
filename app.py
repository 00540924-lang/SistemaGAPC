import streamlit as st
from modulos.login import login
from modulos.menu import mostrar_menu

# ==========================================
# VARIABLES DE SESIÓN
# ==========================================
st.session_state.setdefault("sesion_iniciada", False)
st.session_state.setdefault("page", "menu")

# ==========================================
# LOGIN
# ==========================================
if not st.session_state["sesion_iniciada"]:
    login()
    st.stop()

# ==========================================
# ROUTER PRINCIPAL
# ==========================================
pagina = st.session_state["page"]

if pagina == "menu":
    mostrar_menu()

elif pagina == "usuarios":
    from modulos.registrar_miembros import registrar_miembros
    registrar_miembros()

elif pagina == "proyectos":
    st.title("⚒ Gestión de Proyectos (Aún no implementado)")

elif pagina == "inspecciones":
    st.title("🔍 Inspecciones (Aún no implementado)")

elif pagina == "documentos":
    st.title("📄 Documentos (Aún no implementado)")

elif pagina == "reportes":
    st.title("📊 Reportes (Aún no implementado)")

elif pagina == "configuracion":
    st.title("⚙️ Configuración (Aún no implementado)")

else:
    st.error("❌ Página no encontrada.")

