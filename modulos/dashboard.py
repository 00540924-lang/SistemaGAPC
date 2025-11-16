import streamlit as st

def dashboard():
    st.set_page_config(page_title="Dashboard - GAPC", layout="wide")

    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.sidebar.title("Bienvenido")
    st.sidebar.write(f"Usuario: **{st.session_state.get('usuario', 'Invitado')}**")

    menu = st.sidebar.radio("Navegación", ["Inicio", "Gestión", "Reportes", "Configuración"])

    st.title("📊 Panel Principal del Sistema GAPC")

    st.markdown("""
        <style>
            .card {
                background: white;
                padding: 25px;
                border-radius: 16px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                text-align: center;
            }
            .card h2 {
                color: #2C3E50;
            }
            .card p {
                color: #7F8C8D;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='card'><h2>📁 Módulo 1</h2><p>Gestión de datos</p></div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'><h2>📈 Módulo 2</h2><p>Reportes estadísticos</p></div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='card'><h2>⚙ Configuración</h2><p>Ajustes generales</p></div>", unsafe_allow_html=True)
