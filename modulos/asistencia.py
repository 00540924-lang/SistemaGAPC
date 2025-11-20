import streamlit as st
import mysql.connector
from datetime import date
from modulos.config.conexion import obtener_conexion  # IMPORT CORRECTO

def mostrar_asistencia():

    # Verificar grupo del admin
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

    # Convertimos la lista a un dataframe manipulable
    import pandas as pd
    df_asistencia = pd.DataFrame(miembros)
    df_asistencia["Asistencia"] = "Presente"  # Valor por defecto
    df_asistencia = df_asistencia.rename(columns={
        "Nombre": "Miembro"
    })

    st.subheader("🧑‍🤝‍🧑 Registro de asistencia en tabla")

    # ===============================
    # 4. Tabla editable para marcar asistencia
    # ===============================
    tabla_editada = st.data_editor(
        df_asistencia,
        column_config={
            "Asistencia": st.column_config.SelectboxColumn(
                "Asistencia",
                options=["Presente", "Ausente"],
                required=True
            )
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
        SELECT A.fecha, M.Nombre, A.asistencia
        FROM Asistencia A
        JOIN Miembros M ON A.id_miembro = M.id_miembro
        WHERE A.id_grupo = %s
        ORDER BY A.fecha DESC, M.Nombre
    """, (id_grupo,))

    registros = cursor.fetchall()

    if registros:
        st.dataframe(registros, use_container_width=True)
    else:
        st.info("No hay registros todavía.")

    cursor.close()
    conn.close()

    # -------------------------
    # BOTÓN REGRESAR
    # -------------------------
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
