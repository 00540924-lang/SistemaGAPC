from modulos.login import login
from modulos.dashboard import dashboard
import streamlit as st

if "usuario" not in st.session_state:
    login()
else:
    dashboard()
