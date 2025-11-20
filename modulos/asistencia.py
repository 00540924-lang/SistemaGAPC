import streamlit as st
import mysql.connector
from datetime import date
from modulos.config.conexion import obtener_conexion
import pandas as pd

def mostrar_asistencia():

    # ===============================
    # 0. Verificar grupo del admin
    # ===============================
    id_grupo = st.session_state.get("id_grupo", None)

    if not id_grupo:
        st.error("❌ No se detectó un grupo asignado. Inicie sesión nuevamente.")
        return

    st.title("📋 Registro de Asistencia")

    # ===============================
    # 1. Conexión a la BD
    # ===============================
    conn = obtener_conexion()
    if not conn:
        st.error("❌ No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor(dictionary=True)

    # ===============================
    # 2. Seleccionar fecha
    # ===============================
    fecha = st.date_input("📅 Seleccione la fecha de asistencia", date.today())
    st.write("---")

    # ===============================
    # 3. Obtener miembros del grupo
    # ===============================
    cursor.execute("""
        SELECT M.id_miembro, M.Nombre
        FROM Miembros M
        JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
        ORDER BY M.Nombre
    """, (id_grupo,))

    miembros = cursor.fetchall()

    if not miembros:
        st.warning("⚠️ No hay miembros registrados en este grupo.")
        return

    # ===============================
    # 3.1 Obtener nombre del grupo
    # ===============================
    cursor.execute("SELECT Nombre_grupo FROM Grupos WHERE id_grupo = %s", (id_grupo,))
    grupo_nombre = cursor.fetchone()
    grupo_nombre = grupo_nombre["Nombre_grupo"] if grupo_nombre else f"ID {id_grupo}"

    # ===============================
    # 4. Crear DataFrame editable
    # ===============================
    df_asistencia = pd.DataFrame(miembros)
    df_asistencia = df_asistencia.rename(columns={"Nombre": "Miembro"})
    df_asistencia["Asistencia"] = "Presente"  # valor por defecto

    st.subheader(f"🧑‍🤝‍🧑 Miembros del grupo ({grupo_nombre})")

    tabla_editada = st.data_editor(
        df_asistencia,
        column_config={
            "Asistencia": st.column_config.SelectboxColumn(
                "Asistencia",
                options=["Presente", "Ausente"],
                required=True
            ),
            "id_miembro": None  # OCULTAR COLUMNA
        },
        hide_index=True,
        use_container_width=True,
    )

    st.write("---")

    # ===============================
    # 5. Guardar asistencia
    # ===============================
    if st.button("💾 Guardar asistencia"):

        for _, row in tabla_editada.iterrows():
            cursor.execute("""
                INSERT INTO Asistencia (id_grupo, fecha, id_miembro, asistencia)
                VALUES (%s, %s, %s, %s)
            """, (id_grupo, fecha, row["id_miembro"], row["Asistencia"]))

        conn.commit()
        st.success("✅ Asistencia registrada con éxito")

    # ===============================
    # 6. Historial
    # ===============================
    st.write("---")
    st.subheader("📚 Historial de Asistencias")

    cursor.execute("""
        SELECT A.fecha, M.Nombre
