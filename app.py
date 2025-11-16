import streamlit as st

st.markdown("<h2 style='text-align:center;'>Menú Principal</h2>", unsafe_allow_html=True)

# Estilo de botones grandes
button_style = """
<style>
.big-button {
    width: 100%;
    padding: 20px;
    font-size: 22px;
    border-radius: 12px;
    text-align: center;
    background-color: #4CAF50;
    color: white;
}
.big-button:hover {
    background-color: #45a049;
}
</style>
"""
st.markdown(button_style, unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("📁 Gestión de Datos", key="b1"):
        st.session_state["pag"] = "datos"

with col2:
    if st.button("📊 Análisis", key="b2"):
        st.session_state["pag"] = "analisis"

with col1:
    if st.button("👤 Usuarios", key="b3"):
        st.session_state["pag"] = "usuarios"

with col2:
    if st.button("⚙️ Configuración", key="b4"):
        st.session_state["pag"] = "config"

# Mostrar contenido según selección
if "pag" in st.session_state:
    st.write(f"Has seleccionado: **{st.session_state['pag']}**")


