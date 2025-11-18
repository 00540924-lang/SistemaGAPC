import streamlit as st

# Función para mostrar un "botón con emoji"
def emoji_button(emoji, texto, key, color="#FFFFFF"):
    """
    Crea un botón estilo Streamlit con emoji grande arriba y texto abajo.
    Retorna True si se clickea.
    """
    clicked = False
    col = st.container()
    with col:
        # Markdown para el emoji grande centrado
        st.markdown(f"<div style='font-size:48px;text-align:center;'>{emoji}</div>", unsafe_allow_html=True)
        # Botón real debajo
        if st.button(texto, key=key):
            clicked = True
    return clicked

# Simular un rol
if "rol" not in st.session_state:
    st.session_state["rol"] = "institucional"  # Cambiar para test

rol = st.session_state["rol"]

st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

# Definir módulos
modulos_base = [
    ("📁", "Gestión de Proyectos", "proyectos"),
    ("👥", "Gestión de Usuarios", "usuarios"),
    ("📝", "Grupos", "grupos"),
    ("📄", "Gestión Documental", "documentos"),
    ("📊", "Reportes", "reportes"),
    ("⚙️", "Configuración", "configuracion"),
]

# Filtrar por rol
if rol == "institucional":
    modulos = modulos_base
elif rol == "promotor":
    modulos = [m for m in modulos_base if m[2] in ["proyectos", "grupos"]]
elif rol == "miembro":
    modulos = [m for m in modulos_base if m[2] == "documentos"]
else:
    st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
    modulos = []

# Crear grid de botones
cols = st.columns(3)
for i, (emoji, texto, key) in enumerate(modulos):
    with cols[i % 3]:
        if emoji_button(emoji, texto, key):
            st.session_state.page = key
            st.experimental_rerun()

# Botón de logout
st.write("---")
if st.button("🔒 Cerrar sesión"):
    st.session_state.clear()
    st.experimental_rerun()
