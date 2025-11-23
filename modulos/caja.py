import streamlit as st 
import mysql.connector
from datetime import date
from modulos.config.conexion import obtener_conexion
import pandas as pd
import matplotlib.pyplot as plt

def mostrar_caja(id_grupo):
    """
    Módulo de caja.
    Recibe id_grupo desde app.py (obligatorio para miembros).
    """

    # ===============================
    # 0. Verificar acceso
    # ===============================
    rol = st.session_state.get("rol", "").lower()
    usuario = st.session_state.get("usuario", "").lower()

    if rol not in ["miembro", "institucional"] and usuario != "dark":
        st.error("❌ No tiene permisos para acceder a este módulo.")
        return

    if rol == "miembro" and not id_grupo:
        st.error("❌ No tiene un grupo asignado. Contacte al administrador.")
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
    # 2. Fecha
    # ===============================
    fecha = st.date_input("📅 Fecha de registro", date.today())

    # ===============================
    # 2.1 Cargar multas pagadas automáticas
    # ===============================
    cursor.execute("""
        SELECT COALESCE(SUM(monto_a_pagar), 0) AS total_multas
        FROM Multas MT
        JOIN Miembros M ON MT.id_miembro = M.id_miembro
        JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
        AND MT.fecha = %s
        AND MT.pagada = 1
    """, (id_grupo, fecha))

    resultado_multa = cursor.fetchone()
    multa_auto = float(resultado_multa["total_multas"]) if resultado_multa else 0.0

    st.write("---")

    # ===============================
    # 3. DINERO QUE ENTRA
    # ===============================
    st.subheader("🟩 Dinero que entra")

    st.text_input("Multas PAGADAS del día", value=f"${multa_auto:.2f}", disabled=True)

    multa = multa_auto

    ahorros = st.number_input("Ahorros", min_value=0.0, step=0.01)
    otras_actividades = st.number_input("Otras actividades", min_value=0.0, step=0.01)
    pagos_prestamos = st.number_input("Pago de préstamos (capital e interés)", min_value=0.0, step=0.01)
    otros_ingresos = st.number_input("Otros ingresos del grupo", min_value=0.0, step=0.01)

    total_entrada = multa + ahorros + otras_actividades + pagos_prestamos + otros_ingresos
    st.number_input("🔹 Total dinero que entra", value=total_entrada, disabled=True)

    # ===============================
    # 4. DINERO QUE SALE
    # ===============================
    st.write("---")
    st.subheader("🟥 Dinero que sale")

    retiro_ahorros = st.number_input("Retiros de ahorros", min_value=0.0, step=0.01)
    desembolso = st.number_input("Desembolso de préstamos", min_value=0.0, step=0.01)
    gastos_grupo = st.number_input("Otros gastos del grupo", min_value=0.0, step=0.01)

    total_salida = retiro_ahorros + desembolso + gastos_grupo
    st.number_input("🔻 Total dinero que sale", value=total_salida, disabled=True)

    # ===============================
    # 5. Saldo neto
    # ===============================
    st.write("---")
    saldo_neto = total_entrada - total_salida
    st.number_input("⚖️ Saldo del cierre", value=saldo_neto, disabled=True)

    # ===============================
    # 6. Guardado automático
    # ===============================
    if multa > 0 or ahorros > 0 or otras_actividades > 0 or pagos_prestamos > 0 or otros_ingresos > 0 or total_salida > 0:

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
        st.success("✅ Registro de caja guardado automáticamente.")

    # ===============================
    # 7. Historial
    # ===============================
    st.write("---")
    st.subheader("📚 Historial de Caja")

    cursor.execute("""
        SELECT fecha, total_entrada, total_salida
        FROM Caja
        WHERE id_grupo = %s
        ORDER BY fecha DESC
    """, (id_grupo,))

    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros)
        st.dataframe(df)

    cursor.close()
    conn.close()

    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
