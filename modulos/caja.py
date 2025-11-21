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
    # 7. Historial con gráfico y filtros
    # ===============================
    st.write("---")
    st.subheader("📚 Historial de Caja")
    st.info("Filtre por fecha o deje vacío para ver todos los registros.")

    # Columnas para filtros y botón limpiar
    col1, col2, col3 = st.columns([1,1,1])
    fecha_inicio = col1.date_input("📅 Fecha inicio (opcional)", key="filtro_inicio")
    fecha_fin = col2.date_input("📅 Fecha fin (opcional)", key="filtro_fin")

    # Botón para limpiar filtros usando flag
    if col3.button("🧹 Limpiar filtros"):
        st.session_state["limpiar_filtros"] = True

    # Aplicar filtro vacío si se presionó limpiar
    if st.session_state.get("limpiar_filtros", False):
        fecha_inicio = None
        fecha_fin = None
        st.session_state["limpiar_filtros"] = False

    query = """
        SELECT fecha, total_entrada, total_salida
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
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha').reset_index(drop=True)

        # Reemplazar None o NaN por 0 y convertir a float
        df['total_entrada'] = df['total_entrada'].fillna(0).astype(float)
        df['total_salida'] = df['total_salida'].fillna(0).astype(float)

        fig, ax = plt.subplots(figsize=(10, 5))
        width = 0.35
        x = range(len(df))

        ax.bar([i - width/2 for i in x], df['total_entrada'], width=width, color='#4CAF50', label='Entradas')
        ax.bar([i + width/2 for i in x], df['total_salida'], width=width, color='#F44336', label='Salidas')

        max_entrada = df['total_entrada'].max()
        max_salida = df['total_salida'].max()

        for i, row in df.iterrows():
            entrada_val = float(row['total_entrada'])
            salida_val = float(row['total_salida'])
            ax.text(i - width/2, entrada_val + max_entrada*0.01,
                    f"{entrada_val:.2f}", ha='center', va='bottom', fontsize=8, color='#2E7D32')
            ax.text(i + width/2, salida_val + max_salida*0.01,
                    f"{salida_val:.2f}", ha='center', va='bottom', fontsize=8, color='#B71C1C')

        ax.set_xlabel("Fecha", fontsize=12)
        ax.set_ylabel("Monto", fontsize=12)
        ax.set_title("Historial de Caja: Entradas y Salidas", fontsize=14, weight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in df['fecha']], rotation=45, ha='right', fontsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend()

        saldo_final = df['total_entrada'].sum() - df['total_salida'].sum()
        st.pyplot(fig)
        st.markdown(
            f"""
            <div style="text-align:center; font-size:16px;">
                <span style="color:#4CAF50;"><strong>Entrada total:</strong> {df['total_entrada'].sum():.2f}</span> &nbsp;&nbsp;
                <span style="color:#F44336;"><strong>Salida total:</strong> {df['total_salida'].sum():.2f}</span> &nbsp;&nbsp;
                <span style="color:#0000FF; font-size:18px;"><strong>💰 Saldo final: {saldo_final:.2f}</strong></span>
            </div>
            """, unsafe_allow_html=True
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
