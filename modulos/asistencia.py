import streamlit as st
import mysql.connector
from datetime import datetime
from app import get_connection



# -------------------------------------------------------
#   🔹 Obtener el grupo al que pertenece el usuario
# -------------------------------------------------------
def obtener_id_grupo(id_miembro):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id_grupo FROM GrupoMiembros WHERE id_miembro = %s"
    cursor.execute(query, (id_miembro,))
    resultado = cursor.fetchone()

    cursor.close()
    conn.close()

    if resultado:
        return resultado[0]
    return None


# -------------------------------------------------------
#   🔹 Obtener lista de miembros del grupo
# -------------------------------------------------------
def obtener_miembros_grupo(id_grupo):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT Miembros.id_miembro, Miembros.Nombre
        FROM Miembros
        INNER JOIN GrupoMiembros ON Miembros.id_miembro = GrupoMiembros.id_miembro
        WHERE GrupoMiembros.id_grupo = %s
        ORDER BY Miembros.Nombre ASC
    """
    cursor.execute(query, (id_grupo,))
    miembros = cursor.fetchall()

    cursor.close()
    conn.close()

    return miembros


# -------------------------------------------------------
#   🔹 Registrar asistencia
# -------------------------------------------------------
def guardar_asistencia(id_miembro, id_grupo, estado):
    conn = get_connection()
    cursor = conn.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d")

    query = """
        INSERT INTO Asistencia (id_miembro, id_grupo, fecha, estado)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (id_miembro, id_grupo, fecha, estado))
    conn.commit()

    cursor.close()
    conn.close()


# -------------------------------------------------------
#   🔹 Mostrar asistencia registrada
# -------------------------------------------------------
def obtener_asistencia_grupo(id_grupo):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT Miembros.Nombre, Asistencia.fecha, Asistencia.estado
        FROM Asistencia
        INNER JOIN Miembros ON Asistencia.id_miembro = Miembros.id_miembro
        WHERE Asistencia.id_grupo = %s
        ORDER BY Asistencia.fecha DESC
    """
    cursor.execute(query, (id_grupo,))
    registros = cursor.fetchall()

    cursor.close()
    conn.close()

    return registros


# -------------------------------------------------------
#   🔹 INTERFAZ PRINCIPAL
# -------------------------------------------------------
def mostrar_asistencia():

    # 1️⃣ Validar sesión
    if "id_miembro" not in st.session_state:
        st.error("No se detectó un usuario en sesión. Inicie sesión nuevamente.")
        st.stop()

    id_miembro = st.session_state["id_miembro"]

    # 2️⃣ Obtener grupo del usuario
    id_grupo = obtener_id_grupo(id_miembro)

    if not id_grupo:
        st.error("No se encontró un grupo asociado a este usuario.")
        st.stop()

    st.title("📋 Registro de Asistencia")

    # 3️⃣ Cargar miembros del grupo
    miembros = obtener_miembros_grupo(id_grupo)

    if not miembros:
        st.warning("No hay miembros registrados en este grupo.")
        st.stop()

    nombres = {m[1]: m[0] for m in miembros}

    # 4️⃣ Formulario de asistencia
    st.subheader("Registrar asistencia")

    miembro_sel = st.selectbox("Seleccione un miembro:", list(nombres.keys()))
    estado_sel = st.radio("Estado:", ["Presente", "Ausente"])

    if st.button("Guardar asistencia"):
        guardar_asistencia(nombres[miembro_sel], id_grupo, estado_sel)
        st.success("Asistencia registrada correctamente.")

    st.divider()

    # 5️⃣ Mostrar asistencia del grupo
    st.subheader("Historial de asistencia del grupo")

    registros = obtener_asistencia_grupo(id_grupo)

    if registros:
        st.table(
            {
                "Nombre": [r[0] for r in registros],
                "Fecha": [r[1] for r in registros],
                "Estado": [r[2] for r in registros],
            }
        )
    else:
        st.info("Aún no hay asistencia registrada para este grupo.")


