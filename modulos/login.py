
import streamlit as st
import mysql.connector
from streamlit_extras.switch_page_button import switch_page

def login():
    st.set_page_config(page_title="Sistema GAPC", layout="centered")

    # --- CSS personalizado ---
    st.markdown("""
        <style>
        body { 
            background-color: #f5f5f5;
        }

        .login-card {
            background: white;
            padding: 40px;
            border-radius: 16px;
            max-width: 420px;
            margin: auto;
            box-shadow: 0px 6px 20px rgba(0,0,0,0.1);
        }

        .title {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #2C3E50;
        }

        .subtitle {
            text-align: center;
            color: #7F8C8D;
            font-size: 14px;
            margin-bottom: 25px;
        }

        .stButton>button {
            background-color: #3498db;
            color: white;
            padding: 10px 0px;
            width: 100%;
            border-radius: 8px;
            border: none;
            font-size: 18px;
        }

        .stButton>button:hover {
            background-color: #2980b9;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<p class='title'>🔐 Sistema GAPC</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Inicia sesión para continuar</p>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="gapc"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE Usuario=%s AND Contraseña=%s", 
                           (usuario, contraseña))
            resultado = cursor.fetchone()

            if resultado:
                st.success("Inicio de sesión exitoso ✔")
                st.session_state["usuario"] = usuario
                switch_page("dashboard")
            else:
                st.error("Usuario o contraseña incorrectos")

        except Exception as e:
            st.error("Error al conectar con la base de datos")

    st.markdown("</div>", unsafe_allow_html=True)
