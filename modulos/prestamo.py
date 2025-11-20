import streamlit as st
import mysql.connector
from mysql.connector import Error

def modulo_prestamo():

    # ------------------------------
    # VERIFICAR GRUPO DEL USUARIO
    # ------------------------------
    grupo_usuario = st.session_state.get("grupo")

    if not grupo_usuario:
        st.error("❌ No se detectó el grupo del usuario. Inicie sesión nuevamente.")
        st.stop()

    # ------------------------------
    # CONEXIÓN A BASE DE DATOS
    # ------------------------------
    try:
        conexion = mysql.connector.connect(
            host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
            user="uiazxdhtd3r8o7uv",
            password="uGjZ9MXWemv7vPsjOdA5",
            database="bzn5gsi7ken7lufcglbg"
        )

        cursor = conexion.cursor(dictionary=True)

        # -----------------------------------------------
        # OBTENER MIEMBROS DEL MISMO GRUPO DEL USUARIO
        # -----------------------------------------------
        query = """
            SELECT Miembros.id_miembro, Miembros.Nombre
            FROM Miembros
            JOIN Grupomiembros 
            ON Miembros.id_miembro = Grupomiembros.id_miembro
            WHERE Grupomiembros.id_grupo = %s
        """
        cursor.execute(query, (grupo_usuario,))
        miembros = cursor.fetchall()

    except Error as e:
        st.error(f"Error de conexión: {e}")
        return

    # ---------------------------------------------------
    # FORMULARIO DE PRÉSTAMO
    # ---------------------------------------------------
    st.title("📄 Formulario de Préstamo")

    with st.form("form_prestamo"):

        col1, col2 = st.columns(2)

        with col1:
            fecha_desembolso = st.date_input("Fecha de desembolso")
            proposito = st.text_input("Propósito del préstamo")

        with col2:
            fecha_vencimiento = st.date_input("Fecha de vencimiento")
            cantidad = st.number_input("Cantidad del préstamo", min_value=0.0)

        # Selector de miembros filtrados por grupo
        lista_miembros = [m["Nombre"] for m in miembros]
        socia = st.selectbox("Seleccione la socia / miembro", lista_miembros)

        firma = st.text_input("Firma del responsable")

        submit = st.form_submit_button("💾 Registrar préstamo")

        if submit:
            st.success("✔ Préstamo guardado correctamente.")
            # Aquí puedes insertar los datos en tu tabla de préstamos si ya la tienes

    # ---------------------------------------------------
    # FORMULARIO VISUAL QUE QUIERES MOSTRAR
    # ---------------------------------------------------
    st.markdown("### 📑 Formulario de control de pagos")
    st.image("/mnt/data/2013d973-988f-4087-ad4d-c93023046c52.png", use_column_width=True)
