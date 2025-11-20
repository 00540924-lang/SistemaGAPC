import streamlit as st
import mysql.connector
from datetime import date
from modulos.config.conexion import get_connection   # ← TU FUNCIÓN REAL


def mostrar_asistencia():

    # ========================================================
    # 1. Obtener ID del grupo del usuario
    # ========================================================
    id_grupo = st.session_state.get("id_grupo", None)

    if not id_grupo:
        st.error("❌ No se detectó un grupo asignado. Inicie sesión nuevamente.")
        return

    # Conexión a la base
    conn = get_connection()
    if not conn:
        st.error("❌ No se pudo conectar a MySQL.")
        return

    cursor = conn.cursor(dictionary=True)

    # ========================================================
    # 2. Obtener nombre del grupo
    # ========================================================
    cursor.execute("SELECT nombre FROM Grupos WHERE id_grupo = %s", (id_grupo,))
    grupo = cursor.fetchone()

    if not grupo:
        st.error("❌ No se encontró el grupo.")
        return

    nombre_grupo = grupo["nombre"]

    st.title("📋 Registro de Asistencia")
    st.subheader(f"👥 Miembros del grupo: **{nombre_grupo}**")

    # ========================================================
    # 3. Seleccionar fecha
    # ========================================================
    fecha = st.date_input("📅 Seleccione la fecha", date.today())
    st.write("---")

    # ========================================================
    # 4. Obtener miembros desde la tabla intermedia
    # ========================================================
    cursor.execute("""
        SELECT M.id_miembro, M.Nombre
        FROM Miembros M
        JOIN GrupoMiembros GM ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
        ORDER BY M.Nombre ASC
    """, (id_grupo,))

    miembros = cursor.fetchall()

    if not miembros:
        st.warning("⚠️ No hay miembros asignados al grupo.")
        return

    # ========================================================
    # 5. Mostrar controles estilo tabla
    # ========================================================
    st.write("### 🗒️ Registrar asistencia")

    estado_asistencia = {}

    # Encabezado estilo tabla
    col1, col2 = st.columns([3, 2])
    col1.markdown("**Nombre**")
    col2.markdown("**Asistencia**")

    for m in miembros:
        col1, col2 = st.columns([3, 2])

        with col1:
            st.write(m["Nombre"])

        with col2:
            estado = st.radio(
                f"asistencia_{m['id_miembro']}",
                ["Presente", "Ausente"],
                horizontal=True,
                label_visibility="collapsed"
            )

        estado_asistencia[m["id_miembro"]] = estado

    st.write("---")

    # ========================================================
    # 6. Guardar asistencia
    # ========================================================
    if st.button("💾 Guardar asistencia"):
        for id_m, estado in estado_asistencia.items():
            cursor.execute("""
                INSERT INTO Asistencia (id_grupo, fecha, id_miembro, asistencia)
                VALUES (%s, %s, %s, %s)
            """, (id_grupo, fecha, id_m, estado))

        conn.commit()
        st.success("✅ Asistencia guardada correctamente.")

    # ========================================================
    # 7. Historial de asistencia
    # ========================================================
    st.write("---")
    st.subheader("📚 Historial del grupo")

    cursor.execute("""
        SELECT A.fecha, M.Nombre, A.asistencia
        FROM Asistencia A
        JOIN Miembros M ON A.id_miembro = M.id_miembro
        WHERE A.id_grupo = %s
        ORDER BY A.fecha DESC, M.Nombre ASC
    """, (id_grupo,))

    registros = cursor.fetchall()

    if registros:
        st.dataframe(registros)
    else:
        st.info("Aún no hay registros.")

    cursor.close()
    conn.close()

