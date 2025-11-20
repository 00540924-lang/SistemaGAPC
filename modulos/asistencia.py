import streamlit as st
import mysql.connector
from datetime import date


def mostrar_asistencia():

    # Verificar grupo del admin
    id_grupo = st.session_state.get("id_grupo", None)

    if not id_grupo:
        st.error("❌ No se detectó un grupo asignado. Inicie sesión nuevamente.")
        return

    st.title("📋 Registro de Asistencia")

    # ===============================
    # CONEXIÓN DIRECTa
    # ===============================
    try:
        conn = mysql.connector.connect(
            host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
            user="uiazxdhtd3r8o7uv",
            password="uGjZ9MXWemv7vPsjOdA5",
            database="bzn5gsi7ken7lufcglbg"
        )
        cursor = conn.cursor(dictionary=True)
    except mysql.connector.Error as e:
        st.error(f"❌ Error al conectar con la base de datos: {e}")
        return

    # ===============================
    # 1. Seleccionar fecha
    # ===============================
    fecha = st.date_input("📅 Seleccione la fecha de asistencia", date.today())
    st.write("---")

    # ===============================
    # 2. Obtener miembros del grupo
    # ===============================
    cursor.execute("""
        SELECT id_miembro, Nombre
        FROM Miembros
        WHERE id_grupo = %s
        ORDER BY Nombre
    """, (id_grupo,))

    miembros = cursor.fetchall()

    if not miembros:
        st.warning("⚠️ No hay miembros registrados en este grupo.")
        return

    # ===============================
    # 3. Mostrar lista de asistencia
    # ===============================
    st.subheader("Miembros del grupo")

    estado_asistencia = {}

    for m in miembros:
        estado = st.radio(
            f"{m['Nombre']}",
            ["Presente", "Ausente"],
            horizontal=True,
            key=f"asistencia_{m['id_miembro']}"
        )
        estado_asistencia[m["id_miembro"]] = estado

    st.write("---")

    # ===============================
    # 4. Guardar asistencia
    # ===============================
    if st.button("💾 Guardar asistencia"):

        for id_miembro, estado in estado_asistencia.items():
            cursor.execute("""
                INSERT INTO Asistencia (id_grupo, fecha, id_miembro, asistencia)
                VALUES (%s, %s, %s, %s)
            """, (id_grupo, fecha, id_miembro, estado))

        conn.commit()
        st.success("✅ Asistencia registrada con éxito")

    # ===============================
    # 5. Consultar asistencias anteriores
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
        st.dataframe(registros)
    else:
        st.info("No hay registros todavía.")

    cursor.close()
    conn.close()

