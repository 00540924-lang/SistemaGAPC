import streamlit as st
from modulos.config.conexion import obtener_conexion
import pandas as pd

# Función para obtener los miembros de un grupo
def obtener_socios(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)  # Para obtener diccionarios
    try:
        cursor.execute("""
            SELECT M.id_miembro AS id, M.Nombre AS nombre
            FROM Miembros M
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY M.Nombre
        """, (id_grupo,))
        return cursor.fetchall()
    finally:
        cursor.close()
        con.close()

# Función para guardar las multas
def guardar_multas(multas_data):
    con = obtener_conexion()
    cursor = con.cursor()
    try:
        for multa in multas_data:
            cursor.execute(
                """
                INSERT INTO Multas (id_miembro, fecha, monto_a_pagar, pagada)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    monto_a_pagar = VALUES(monto_a_pagar),
                    pagada = VALUES(pagada)
                """,
                (multa['id_miembro'], multa['fecha'], multa['monto_a_pagar'], multa['pagada'])
            )
        con.commit()
    finally:
        cursor.close()
        con.close()

# ===================================
# Función principal del módulo multas
# ===================================
def multas_modulo():
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]
    socios = obtener_socios(id_grupo)

    st.title("📄 Formulario de Multas")

    fechas = ["2025-01-15", "2025-02-15", "2025-03-15", "2025-04-15"]  # ajusta según necesites

    with st.form("form_multas"):
        multas_data = []

        for idx, socio in enumerate(socios, start=1):
            st.write(f"**{idx}. {socio['nombre']}**")
            for fecha in fechas:
                col1, col2 = st.columns(2)
                with col1:
                    monto_a_pagar = st.number_input(
                        f"Monto a pagar {fecha} (Socio {socio['nombre']})",
                        min_value=0.0, step=0.01,
                        key=f"monto_pagar_{socio['id']}_{fecha}"
                    )
                with col2:
                    pagada = st.checkbox(
                        f"Pagada {fecha} (Socio {socio['nombre']})",
                        key=f"pagada_{socio['id']}_{fecha}"
                    )
                multas_data.append({
                    "id_miembro": socio["id"],
                    "fecha": fecha,
                    "monto_a_pagar": monto_a_pagar,
                    "pagada": 1 if pagada else 0
                })

        enviar = st.form_submit_button("Guardar Multas")

    if enviar:
        guardar_multas(multas_data)
        st.success("Multas guardadas correctamente ✔️")
        st.experimental_rerun()
