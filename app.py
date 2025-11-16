import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

# ------------------ CSS ESTILO APP MÓVIL ------------------
st.markdown("""
    <style>

    /* Ocultar menú y header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fondo tipo app móvil */
    body {
        background: linear-gradient(160deg, #0D0D0D 0%, #1A1A1A 40%, #2A2A2A 100%);
        color: #FFFFFF;
        font-family: 'Arial', sans-serif;
    }

    /* Contenedor tipo app */
    .mobile-card {
        background: #111111;
        width: 90%;
        max-width: 380px;
        margin: 80px auto;
        padding: 35px 25px;
        border-radius: 28px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.6);
        animation: slideUp .7s ease;
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }

