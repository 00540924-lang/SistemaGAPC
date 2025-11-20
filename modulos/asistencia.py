import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# ==========================================
# CONEXIÓN A LA BASE DE DATOS
# ==========================================
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
            user="uiazxdhtd3r8o7uv",
            password="uGjZ9MXWemv7vPsjOdA5",
            database="bzn5gsi7ken7lufcglbg"
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"❌ Error al conectar con MySQL: {e}")
        return None


# ==========================================
# MOSTRAR ASISTENCIA
# ==========================================
def mostrar_asistencia():
    st.title("📋 Control de Asistencia")

    # Obtener variables de sesión
    id_grupo = st.session_state.get("id_grupo", None)
    nombre_grupo = st.session_state.get("nombre_grupo", "Sin nombre")

    if not id_grupo:
        st.error("❌ No se detectó el grupo del usuario. Inicie sesión nuevamente.")
        return

    st.subheader(f"Miembros del grupo **{nombre_grupo}**")

    # ---------------------------------------------------
    # Cargar miembros del grupo
    # ---------------------------------------------------
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_miembro, nombre FROM Miembros WHERE id_grupo = %s", (id_grupo,))
    miembros = cursor.fetchall()

    if not miembros:
        st.warning("⚠️ No hay miembros registrados en este grupo.")
        return

    # Convertir a DataFrame para mostrar tabla editable
    df = pd.DataFrame(miembros)
    df["Asistencia"] = "Presente"  # Default

    st.write("### 📌 Lista de asistencia")
    
    edit_df = st.data_editor(
        df,
        hide_index=True,
        column_config={
            "nombre": "Nombre del miembro",
            "Asistencia": st.column_config.SelectboxColumn(
                "Asistencia",
                options=["Presente", "Ausente"],
                help="Selecciona si el miembro asistió o no"
            )
        }
    )

    # ---------------------------------------------------
    # Guardar asistencia
    # ---------------------------------------------------
    if st.button("💾 Guardar asistencia"):
        fecha = datetime.now().strftime("%Y-%m-%d")

        try:
            for _, row in edit_df.iterrows():
                cursor.execute("""
                    INSERT INTO Asistencia (id_miembro, fecha, estado)
                    VALUES (%s, %s, %s)
                """, (row["id_miembro"], fecha, row["Asistencia"]))

            conn.commit()
            st.success("✅ Asistencia guardada correctamente")

        except mysql.connector.Error as e:
            st.error(f"❌ Error al guardar asistencia: {e}")

        finally:
            cursor.close()
            conn.close()

