import streamlit as st
import mysql.connector
from datetime import date
from modulos.config.conexion import obtener_conexion
import pandas as pd

def mostrar_caja():

    # ===============================
    # 0. Verificar grupo por tipo de usuario
    # ===============================
    rol = st.session_state.get("rol", "").lower()
    usuario = st.session_state.get("usuario", "").lower()
    id_grupo = st.session_state.get("id_grupo", None)

    # 🔹 "dark" y "institucional" pueden entrar aunque no tengan grupo
    if usuario != "dark" and rol not in ["institucional"]:
        if not id_grupo:
            st.error("❌ No tiene un grupo asignado. Pida al administrador que lo agregue a un grupo.")
            return

    st.title("💰 Formulario de Caja")

    # ===============================
    # 1. Conexión BD
    # ===============================
    conn = obtener_conexion()
    if not conn:
        st.error("❌ Error al conectar a la base de datos.")
        return
    cursor = conn.cursor(dictionary=True)

    # ===============================
    # 2. Seleccionar fecha
    # ===============================
    fecha = st.date_input("📅 Fecha de registro", date.today())
    st.write("---")

    # ===============================
    # 3. Formulario DINERO QUE ENTRA
    # ===============================
    st.subheader("🟩 Dinero que entra")

    multa = st.number_input("Multas pagadas", min_value=0.0, step=0.01)
    ahorros = st.number_input("Ahorros", min_value=0.0, step=0.01)
    otras_actividades = st.number_input("Otras actividades", min_value=0.0, step=0.01)
    pagos_prestamos = st.number_input("Pago de préstamos (capital e interés)", min_value=0.0, step=0.01)
    otros_ingresos = st.number_input("Otros ingresos del grupo", min_value=0.0, step=0.01)

    total_entrada = multa + ahorros + otras_actividades + pagos_prestamos + otros_ingresos
    st.number_input("🔹 Total dinero que entra", value=total_entrada, disabled=True)

    # ===============================
    # 4. Formulario DINERO QUE SALE
    # ===============================
    st.write("---")
    st.subheader("🟥 Dinero que sale")

    retiro_ahorros = st.number_input("Retiros de ahorros", min_value=0.0, step=0.01)
    desembolso = st.number_input("Desembolso de préstamos", min_value=0.0, step=0.01)
    gastos_grupo = st.number_input("Otros gastos del grupo", min_value=0.0, step=0.01)

    total_salida = retiro_ahorros + desembolso + gastos_grupo
    st.number_input("🔻 Total dinero que sale", value=total_salida, disabled=True)

    # ===============================
    # 5. Calcular saldo neto
    # ===============================
    st.write("---")
    saldo_neto = total_entrada - total_salida
    st.number_input("⚖️ Saldo del cierre", value=saldo_neto, disabled=True)

    # ===============================
    # 6. Guardar registros
    # ===============================
    if st.button("💾 Guardar registro de caja"):

        cursor.execute("""
            INSERT INTO Caja (
                id_grupo, fecha, multas, ahorros, otras_actividades, 
                pago_prestamos, otros_ingresos, total_entrada,
                retiro_ahorros, desembolso, gastos_grupo, total_salida,
                saldo_cierre
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            id_grupo, fecha,
            multa, ahorros, otras_actividades,
            pagos_prestamos, otros_ingresos, total_entrada,
            retiro_ahorros, desembolso, gastos_grupo, total_salida,
            saldo_neto
        ))

        conn.commit()
        st.success("✅ Movimiento de caja guardado con éxito.")

    # ===============================
    # 7. HISTORIAL
    # ===============================
    st.write("---")
    st.subheader("📚 Historial de Caja")

    fecha_filtro = st.date_input(
        "📅 Filtrar por fecha",
        value=None,
        key="filtro_caja"
    )

    if fecha_filtro:
        cursor.execute("""
            SELECT *
            FROM Caja
            WHERE id_grupo = %s AND fecha = %s
            ORDER BY fecha DESC
        """, (id_grupo, fecha_filtro))
    else:
        cursor.execute("""
            SELECT *
            FROM Caja
            WHERE id_grupo = %s
            ORDER BY fecha DESC
        """, (id_grupo,))

    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay registros para mostrar.")

    # ===============================
    # 8. Botón regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    cursor.close()
    conn.close()
