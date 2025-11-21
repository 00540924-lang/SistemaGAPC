import streamlit as st 
import mysql.connector
from datetime import date
from modulos.config.conexion import obtener_conexion
import pandas as pd

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

    # Solo miembros, institucional y Dark pueden usar Caja
    if rol not in ["miembro", "institucional"] and usuario != "dark":
        st.error("❌ No tiene permisos para acceder a este módulo.")
        return

    # Los miembros deben tener grupo sí o sí
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
    st.write("---")

    # ===============================
    # 3. DINERO QUE ENTRA
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
    # 7. Historial
    # ===============================
    st.write("---")
    st.subheader("📚 Historial de Caja")
    st.info("Filtre por fecha o deje vacío para ver todos los registros.")

    # Filtrado por rango de fechas
    col1, col2 = st.columns(2)
    fecha_inicio = col1.date_input("📅 Fecha inicio (opcional)", key="filtro_inicio")
    fecha_fin = col2.date_input("📅 Fecha fin (opcional)", key="filtro_fin")

    query = """
        SELECT fecha, multas, ahorros, otras_actividades, pago_prestamos, otros_ingresos, 
               total_entrada, retiro_ahorros, desembolso, gastos_grupo, total_salida, saldo_cierre
        FROM Caja
        WHERE id_grupo = %s
    """
    params = [id_grupo]

    if fecha_inicio and fecha_fin:
        query += " AND fecha BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])
    elif fecha_inicio:
        query += " AND fecha >= %s"
        params.append(fecha_inicio)
    elif fecha_fin:
        query += " AND fecha <= %s"
        params.append(fecha_fin)

    query += " ORDER BY fecha DESC"

    cursor.execute(query, tuple(params))
    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros)

        # Colores condicionales para resaltar entradas, salidas y saldo
        def highlight_row(row):
            return [
                'background-color: #d4edda' if col in ['multas','ahorros','otras_actividades','pago_prestamos','otros_ingresos','total_entrada'] and row[col] > 0 else
                'background-color: #f8d7da' if col in ['retiro_ahorros','desembolso','gastos_grupo','total_salida'] and row[col] > 0 else
                'background-color: #cce5ff' if col == 'saldo_cierre' else ''
                for col in df.columns
            ]

        st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

        # Mostrar totales
        st.markdown(
            f"**Totales:** Entrada = {df['total_entrada'].sum():.2f}, Salida = {df['total_salida'].sum():.2f}, Saldo final = {df['saldo_cierre'].sum():.2f}"
        )
    else:
        st.info("No hay registros para mostrar.")

    # ===============================
    # 8. Regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    cursor.close()
    conn.close()

