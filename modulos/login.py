import time
import streamlit as st

def login():
    st.set_page_config(page_title="Login", layout="centered")

    # ===== PANTALLA DE CARGA (PRELOADER) =====
    preloader = st.empty()

    preloader.markdown("""
        <style>
        .loader-container {
            margin-top: 160px;
            text-align: center;
            color: white;
            font-family: Arial, sans-serif;
        }

        .loader {
            border: 6px solid #f3f3f3;
            border-top: 6px solid #00d2ff;
            border-radius: 50%;
            width: 65px;
            height: 65px;
            animation: spin 1s linear infinite;
            margin-left: auto;
            margin-right: auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loader-text {
            margin-top: 18px;
            font-size: 22px;
            letter-spacing: 1px;
            animation: fadeIn 2s ease infinite alternate;
        }

        @keyframes fadeIn {
            from { opacity: 0.4; }
            to { opacity: 1; }
        }
        </style>

        <div class="loader-container">
            <div class="loader"></div>
            <div class="loader-text">Cargando...</div>
        </div>
    """, unsafe_allow_html=True)

    # Mostrar el preloader por 1.5 segundos
    time.sleep(1.5)

    # Limpiar el preloader
    preloader.empty()
    # A partir de aquí empieza tu interfaz después del loader
    st.markdown("<h1 style='text-align:center;color:white;'>Bienvenido</h1>", unsafe_allow_html=True)

    Usuario = st.text_input("Usuario")
    Contraseña = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión"):
        ...
