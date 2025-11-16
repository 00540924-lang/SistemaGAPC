import sys
import os

# Asegurar que la ruta raíz esté en sys.path (necesario para Streamlit Cloud)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st
from modulos.login import login

login()

