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

    # ===============================
    # 4. Mostrar controles de asistencia (UI Mejorada)
    # ===============================
    st.subheader("🧑‍🤝‍🧑 Lista de Miembros")

    # CSS para estilizar
    st.markdown("""
    <style>
    .member-card {
        padding: 15px;
        border-radius: 10px;
        background-color: #f7f7f9;
        border: 1px solid #ddd;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .member-name {
        font-size: 16px;
        font-weight: 600;
        color: #333;
    }

    .stRadio > div {
        display: flex !important;
        gap: 10px;
        justify-content: center;
    }

    </style>
    """, unsafe_allow_html=True)

    estado_asistencia = {}

    cols = st.columns(2)  # Se mostrará en dos columnas para mejor organización

    for idx, m in enumerate(miembros):
        col = cols[idx % 2]

        with col:
            st.markdown(f"""
            <div class="member-card">
                <span class="member-name">{m['Nombre']}</span>
            </div>
            """, unsafe_allow_html=True)

            estado = st.radio(
                f"Estado_{m['id_miembro']}",
                ["Presente", "Ausente"],
                key=f"asistencia_{m['id_miembro']}",
                horizontal=True,
                label_visibility="collapsed"
            )

            estado_asistencia[m["id_miembro"]] = estado

    st.write("---")

    # ===============================
    # 5. Guardar asistencia
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
        st.dataframe(registros)
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
