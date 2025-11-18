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

/* --- ESTILO BASE DE TODAS LAS TARJETAS --- */
.card {
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

/* Animación hover */
.card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0px 6px 20px rgba(0,0,0,0.18);
}

/* --- COLORES INDIVIDUALES POR MÓDULO --- */
.card-proyectos { background: #FFF3C4; }      /* Amarillo suave */
.card-usuarios { background: #DDEBFF; }        /* Azul claro */
.card-inspecciones { background: #FFE1E1; }    /* Rojo suave */
.card-documentos { background: #F3E8FF; }      /* Morado suave */
.card-reportes { background: #DFFFE2; }        /* Verde suave */
.card-config { background: #F2F2F2; }          /* Gris claro */
.card-logout { background: #FCE8FF; }          /* Rosa suave */
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='menu-title'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)


# ------------------- FILA 1 -------------------
col1, col2, col3 = st.columns([1,1,1])

with col1:
    with stylable_container(key="proyectos", css_classes=["card", "card-proyectos"]):
        if st.button("📁  Gestión de Proyectos", key="btn_proy"):
            st.switch_page("pages/1_📁_Gestion_de_Proyectos.py")

with col2:
    with stylable_container(key="usuarios", css_classes=["card", "card-usuarios"]):
        if st.button("👥  Gestión de Usuarios", key="btn_users"):
            st.switch_page("pages/2_👥_Gestion_de_Usuarios.py")

with col3:
    with stylable_container(key="insp", css_classes=["card", "card-inspecciones"]):
        if st.button("📝  Inspecciones y Evaluaciones", key="btn_insp"):
            st.switch_page("pages/3_📝_Inspecciones.py")


# ------------------- FILA 2 -------------------
col4, col5, col6 = st.columns([1,1,1])

with col4:
    with stylable_container(key="docs", css_classes=["card", "card-documentos"]):
        if st.button("📄  Gestión Documental", key="btn_docs"):
            st.switch_page("pages/4_📄_Gestion_Documental.py")

with col5:
    with stylable_container(key="reportes", css_classes=["card", "card-reportes"]):
        if st.button("📊  Reportes", key="btn_reports"):
            st.switch_page("pages/5_📊_Reportes.py")

with col6:
    with stylable_container(key="config", css_classes=["card", "card-config"]):
        if st.button("⚙️  Configuración", key="btn_conf"):
            st.switch_page("pages/6_⚙️_Configuracion.py")


# ------------------- SEPARADOR -------------------
st.markdown("<hr style='margin:40px 0;'>", unsafe_allow_html=True)


# ------------------- BOTÓN DE SALIR -------------------
col7, col8, col9 = st.columns([1,1,1])

with col2:
    with stylable_container(key="logout", css_classes=["card", "card-logout"]):
        if st.button("🔒  Cerrar sesión", key="btn_logout"):
            st.switch_page("Login.py")

