import streamlit as st
from modulos.config.conexion import obtener_conexion


# -------------------------------------------------
# FUNCIÓN PARA VERIFICAR USUARIO EN LA BASE DE DATOS
# -------------------------------------------------
def verificar_usuario(usuario, contraseña):
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()

        query = "SELECT Usuario FROM Administradores WHERE Usuario = %s AND Contraseña = %s"
        cursor.execute(query, (usuario, contraseña))
        result = cursor.fetchone()

        return result[0] if result else None

    finally:
        con.close()


# -------------------------------------------------
# PANTALLA DE LOGIN
# ----------------------------------
