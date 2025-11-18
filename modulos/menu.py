import streamlit as st
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(page_title="Menú Principal", layout="wide")

st.markdown("""
<style>
.menu-title {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 40px;
    margin-top: -20px;
}

.card-base {
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    color: #3b3b3b;
    font-size: 20px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.25s ease-in-out;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.10);
    height: 130px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.card-base:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0px 6px 20px rgba(0,0,0,0.18);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='menu-title'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

# -------- COLORES --------
colores = {
    "proyectos": "#FFF3C4",
    "usuarios": "#DDEBFF",
    "inspecciones": "#FFE1E1",
    "documentos": "#F3E8FF",
    "reportes": "#DFFFE2",
    "config": "#F2F2F2",
    "logout": "#FCE8FF"
}

# ------------------- FILA 1 -------------------
col1, col2, col3 = st.columns(3)

with col1:
    with stylable_container("proy", css_styles=f"""
        background-color: {colores['proyectos']};
    """):
        st.markdown("<div class='card-base'>📁 Gestión de Proyectos</div>", unsafe_allow_html=True)
        if st.button(" ", key="btn_proy"):
            st.switch_page("pages/1_📁_Gestion_de_Proyectos.py")

with col2:
    with stylable_container("usuarios", css_styles=f"""
        background-color: {colores['usuarios']};
    """):
        st.markdown("<div class='card-base'>👥 Gestión de Usuarios</div>", unsafe_allow_html=True)
        if st.button(" ", key="btn_users"):
            st.switch_page("pages/2_👥_Gestion_de_Usuarios.py")

with col3:
    with stylable_container("insp", css_styles=f"""
        background-color: {colores['inspecciones']};
    """):
        st.markdown("<div class='card-base'>📝 Inspecciones y Evaluaciones</div>", unsafe_allow_html=True)
        if st.button(" ", key="btn_insp"):
            st.switch_page("pages/3_📝_Inspecciones.py")


# ------------------- FILA 2 -------------------
col4, col5, col6 = st.columns(3)

with col4:
    with stylable_container("docs", css_styles=f"""
        background-color: {colores['documentos']};
    """):
        st.markdown("<div class='card-base'>📄 Gestión Documental</div>", unsafe_allow_html=True)
        if st.button(" ", key="btn_docs"):
            st.switch_page("pages/4_📄_Gestion_Documental.py")

with col5:
    with stylable_container("reportes", css_styles=f"""
        background-color: {colores['reportes']};
    """):
        st.markdown("<div class='card-base'>📊 Reportes</div>", unsafe_allow_html=True)
        if st.button(" ", key="btn_reports"):
            st.switch_page("pages/5_📊_Reportes.py")

with col6:
    with stylable_container("config", css_styles=f"""
        background-color: {colores['config']};
    """):
        st.markdown("<div class='card-base'>⚙️ Configuración</div>", unsafe_allow_html=True)
        if st.button(" ", key="btn_conf"):
            st.switch_page("pages/6_⚙️_Configuracion.py")


# ------------------- LOGOUT -------------------
st.markdown("<hr>", unsafe_allow_html=True)

colL, _, _ = st.columns(3)

with colL:
    with stylable_container("logout", css_styles=f"""
        background-color: {colores['logout']};
    """):
        st.markdown("<div class='card-base'>🔒 Cerrar sesión</div>", unsafe_allow_html=True)
        if st.button(" ", key="btn_logout"):
            st.switch_page("Login.py")
