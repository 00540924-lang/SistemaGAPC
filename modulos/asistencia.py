import streamlit as st
import mysql.connector
from datetime import datetime
from modulos.db import get_connection   # Usa tu función real de conexión


def mostrar_asistencia():

    st.title("📋 Control de Asistencia")

    # ---------------------------------------------
    # 1️⃣ OBTENER ID DEL GRUPO DESDE LA SESIÓN
    # ---------------------------------------------
    id_grupo = st.session_state.get("id_grupo", None)

    if not id_grupo:
        st.error("❌ No se detectó un grupo asociado al usuario. Inicie sesión nuevamente.")
        return

    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()

    # ------------------------------------------------
    # 2️⃣ OBTENER NOMBRE DEL GRUPO
    # ------------------------------------------------
    cursor.execute("SELECT nombre FROM Grupos WHERE id_grupo = %s", (id_grupo,))
    grupo = cursor.fetchone()

    if not grupo:
        st.error("❌ No se encontró información del grupo.")
        return

    nombre_grupo = grupo[0]

    st.subheader(f"👥 Miembros del grupo: **{nombre_grupo}**")

    # ------------------------------------------------
    # 3️⃣ OBTENER MIEMBROS DEL GRUPO (TABLA INTERMEDIA)
    # ------------------------------------------------
    query = """
        SELECT M.id_miembro, M.nombre
        FROM Grupo_Miembros GM
        INNER JOIN Miembros M ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
        ORDER BY M.nombre ASC
    """
    cursor.execute(query, (id_grupo,))
    miembros = cursor.fetchall()

    if not miembros:
        st.warning("⚠ No hay miembros registrados en este grupo.")
        return

    # ------------------------------------------------
    # 4️⃣ MOSTRAR TABLA DE ASISTENCIA
    # ------------------------------------------------
    st.write("### 🗒️ Registrar asistencia")

    asistencia_data = {}

    for id_miembro, nombre in miembros:
        col1, col2 = st.columns([3, 2])

        with col1:
            st.write(f"**{nombre}**")

        with col2:
            estado = st.radio(
                f"Estado_{id_miembro}",
                ["Presente", "Ausente"],
                horizontal=True,
                label_visibility="collapsed"
            )

        asistencia_data[id_miembro] = estado

    # ------------------------------------------------
    # 5️⃣ GUARDAR ASISTENCIA EN BD
    # ------------------------------------------------
    if st.button("💾 Guardar asistencia"):
        fecha = datetime.now().date()

        for id_miembro, estado in asistencia_data.items():
            cursor.execute("""
                INSERT INTO Asistencia (id_miembro, fecha, estado)
                VALUES (%s, %s, %s)
            """, (id_miembro, fecha, estado))

        conn.commit()
        st.success("✅ Asistencia registrada correctamente.")

    cursor.close()
    conn.close()

