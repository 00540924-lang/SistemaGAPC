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

    # 🔹 Solo miembros, institucional y Dark pueden usar Caja
    if rol not in ["miembro", "institucional"] and usuario != "dark":
        st.error("❌ No tiene permisos para acceder a este módulo.")
        return

    # 🔹 Los miembros deben tener grupo sí o sí
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
    # 7. HISTORIAL BONITO
    # ===============================
    st.write("---")
    st.subheader("📚 Historial de Caja")

    st.info("Si desea ver todos los registros, deje la fecha vacía.")

    fecha_filtro = st.date_input(
        "📅 Filtrar por fecha específica (opcional)",
        value=None,
        key="filtro_caja"
    )

    # Consulta SQL
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

    if not registros:
        st.warning("No hay registros disponibles para este filtro.")
    else:
        for r in registros:
            st.markdown("""
                <div style="
                    background:#F8F9FF;
                    padding:20px;
                    border-radius:12px;
                    margin-bottom:15px;
                    border-left: 6px solid #4C3A60;
                ">
                    <h3 style="margin:0; color:#4C3A60;">📅 {fecha}</h3>
                    <p style="margin:4px 0 10px; color:#6D4C41;">Registro de caja del grupo</p>

                    <div style="display:flex; gap:20px;">

                        <div style="
                            flex:1;
                            background:#E8FFF3;
                            padding:15px;
                            border-radius:10px;
                            border:1px solid #B6F2D0;
                        ">
                            <h4 style="color:#15653B; margin:0;">🟩 Entradas</h4>
                            <p><b>Multas:</b> ${multa}</p>
                            <p><b>Ahorros:</b> ${ahorros}</p>
                            <p><b>Otras actividades:</b> ${act}</p>
                            <p><b>Préstamos pagados:</b> ${pp}</p>
                            <p><b>Otros ingresos:</b> ${oi}</p>
                            <p><b>Total entrada:</b> <span style="color:#0B893E;"><b>${te}</b></span></p>
                        </div>

                        <div style="
                            flex:1;
                            background:#FFECEC;
                            padding:15px;
                            border-radius:10px;
                            border:1px solid #F7C0C0;
                        ">
                            <h4 style="color:#B22424; margin:0;">🟥 Salidas</h4>
                            <p><b>Retiros ahorros:</b> ${ra}</p>
                            <p><b>Desembolsos:</b> ${des}</p>
                            <p><b>Gastos del grupo:</b> ${gg}</p>
                            <p><b>Total salida:</b> <span style="color:#C21818;"><b>${ts}</b></span></p>
                        </div>
                    </div>

                    <h3 style="margin-top:15px;">⚖️ Saldo final: 
                        <span style="color:{saldo_color};">
                            <b>${saldo}</b>
                        </span>
                    </h3>
                </div>
            """.format(
                fecha=r["fecha"],
                multa=r["multas"],
                ahorros=r["ahorros"],
                act=r["otras_actividades"],
                pp=r["pago_prestamos"],
                oi=r["otros_ingresos"],
                te=r["total_entrada"],
                ra=r["retiro_ahorros"],
                des=r["desembolso"],
                gg=r["gastos_grupo"],
                ts=r["total_salida"],
                saldo=r["saldo_cierre"],
                saldo_color="#008000" if r["saldo_cierre"] >= 0 else "#C21818"
            ), unsafe_allow_html=True)


    # ===============================
    # 8. Regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    cursor.close()
    conn.close()
