import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import datetime
import time

# =====================================================
#   MÓDULO PRINCIPAL DE PRÉSTAMOS
# =====================================================
def prestamos_modulo():

    # --------------------------------------
    # Validar sesión y grupo
    # --------------------------------------
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]

    # TÍTULO
    st.markdown("<h1 style='text-align:center;'>💲 Gestión de Préstamos</h1>", unsafe_allow_html=True)

    # --------------------------------------
    # Obtener nombre del grupo
    # --------------------------------------
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("SELECT Nombre_grupo FROM Grupos WHERE id_grupo = %s", (id_grupo,))
    grupo = cursor.fetchone()
    con.close()

    nombre_grupo = grupo[0] if grupo else "Grupo desconocido"

    # Mostrar nombre debajo del título
    st.markdown(
        f"<h3 style='text-align:center; color:#555;'>Grupo: {nombre_grupo}</h3>",
        unsafe_allow_html=True
    )

    # --------------------------------------
    # Obtener valores del reglamento
    # --------------------------------------
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT interes_por_10
        FROM Reglamento
        WHERE id_grupo = %s
        LIMIT 1
    """, (id_grupo,))
    reglamento = cursor.fetchone()
    con.close()

    interes_por_10 = float(reglamento[0]) if reglamento else 0.0

    # --------------------------------------
    # Obtener miembros del grupo
    # --------------------------------------
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT M.id_miembro, M.nombre, M.dui
        FROM Miembros M
        JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
    """, (id_grupo,))
    miembros = cursor.fetchall()
    con.close()

    if not miembros:
        st.warning("⚠ No hay miembros registrados en este grupo.")
        return

    miembros_dict = {m[1]: m[0] for m in miembros}

    # =====================================================
    #   FORMULARIO: REGISTRAR NUEVO PRÉSTAMO
    # =====================================================
    with st.form("form_nuevo_prestamo"):
        st.subheader("📄 Nuevo Préstamo")

        miembro_seleccionado = st.selectbox("Selecciona un miembro", list(miembros_dict.keys()))
        proposito = st.text_input("Propósito del préstamo")
        monto = st.number_input("Monto del préstamo", min_value=0.01, step=0.01)
        fecha_desembolso = st.date_input("Fecha de desembolso", datetime.date.today())
        fecha_vencimiento = st.date_input("Fecha de vencimiento", datetime.date.today())

        # Calcular y mostrar interés automáticamente
        interes_total = (monto / 10) * interes_por_10
        monto_total = monto + interes_total
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Capital", f"${monto:,.2f}")
        with col2:
            st.metric("📈 Interés Total", f"${interes_total:,.2f}")
        with col3:
            st.metric("💵 Total a Pagar", f"${monto_total:,.2f}")

        estado = st.selectbox("Estado inicial", ["Activo", "Pendiente"])

        enviar = st.form_submit_button("💾 Guardar Préstamo")

    # BOTÓN REGRESAR - FUERA DEL FORMULARIO
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
    st.write("---")

    if enviar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            # INSERT del préstamo
            cursor.execute("""
                INSERT INTO prestamos (id_miembro, proposito, monto, fecha_desembolso, 
                                     fecha_vencimiento, estado, interes_total, saldo_pendiente)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                miembros_dict[miembro_seleccionado],
                proposito,
                monto,
                fecha_desembolso,
                fecha_vencimiento,
                estado.lower(),
                interes_total,
                monto_total  # Saldo pendiente inicial = monto total
            ))

            con.commit()
            st.success("✅ Préstamo registrado correctamente")
            st.info(f"💰 Total a pagar: ${monto_total:,.2f} (Capital: ${monto:,.2f} + Interés: ${interes_total:,.2f})")
            time.sleep(2)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar préstamo: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'con' in locals() and con.is_connected():
                con.close()

    # Mostrar lista de préstamos y formulario de pagos
    mostrar_lista_prestamos(id_grupo)


# =====================================================
#   TABLA DE PRÉSTAMOS CON CONTROL DE PAGOS
# =====================================================
def mostrar_lista_prestamos(id_grupo):

    con = obtener_conexion()
    cursor = con.cursor()

    # Obtener préstamos con información de pagos
    cursor.execute("""
        SELECT 
            P.id_prestamo, 
            M.nombre, 
            P.proposito, 
            P.monto,
            P.fecha_desembolso, 
            P.fecha_vencimiento, 
            P.estado, 
            P.interes_total,
            P.saldo_pendiente,
            COALESCE(SUM(PP.capital), 0) as total_pagado,
            COUNT(PP.id_pago) as numero_pagos
        FROM prestamos P
        JOIN Miembros M ON M.id_miembro = P.id_miembro
        JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
        LEFT JOIN prestamo_pagos PP ON PP.id_prestamo = P.id_prestamo
        WHERE GM.id_grupo = %s
        GROUP BY P.id_prestamo, M.nombre, P.proposito, P.monto,
                 P.fecha_desembolso, P.fecha_vencimiento, P.estado, 
                 P.interes_total, P.saldo_pendiente
        ORDER BY P.estado, P.id_prestamo DESC
    """, (id_grupo,))

    prestamos = cursor.fetchall()
    con.close()

    if not prestamos:
        st.info("No hay préstamos registrados en este grupo.")
        return

    # Mostrar resumen general
    st.subheader("📊 Resumen de Préstamos")
    
    total_prestamos = len(prestamos)
    prestamos_activos = sum(1 for p in prestamos if p[6] == 'activo')
    total_prestado = sum(p[3] for p in prestamos)
    total_pendiente = sum(p[8] for p in prestamos)
    total_pagado = sum(p[9] for p in prestamos)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Total Préstamos", total_prestamos)
    with col2:
        st.metric("🔄 Activos", prestamos_activos)
    with col3:
        st.metric("💰 Total Prestado", f"${total_prestado:,.2f}")
    with col4:
        st.metric("💵 Pendiente", f"${total_pendiente:,.2f}")

    st.write("---")

    # Tabla detallada de préstamos
    st.subheader("📋 Detalle de Préstamos")
    
    df = pd.DataFrame(prestamos, columns=[
        "ID", "Miembro", "Propósito", "Monto", "Fecha Desembolso", 
        "Fecha Vencimiento", "Estado", "Interés Total", "Saldo Pendiente", 
        "Total Pagado", "Número de Pagos"
    ])

    # Formatear columnas monetarias
    df["Monto"] = df["Monto"].apply(lambda x: f"${x:,.2f}")
    df["Interés Total"] = df["Interés Total"].apply(lambda x: f"${x:,.2f}")
    df["Saldo Pendiente"] = df["Saldo Pendiente"].apply(lambda x: f"${x:,.2f}")
    df["Total Pagado"] = df["Total Pagado"].apply(lambda x: f"${x:,.2f}")

    st.dataframe(df, use_container_width=True)

    # Selección de préstamo para pagos
    st.subheader("💳 Registrar Pago")
    
    prestamo_opciones = {}
    for row in prestamos:
        texto_opcion = f"{row[1]} - ${row[8]:,.2f} pendientes (Pagado: ${row[9]:,.2f}) - {row[2]}"
        prestamo_opciones[texto_opcion] = row[0]

    if prestamo_opciones:
        prestamo_sel = st.selectbox("Selecciona un préstamo:", list(prestamo_opciones.keys()))
        
        if prestamo_sel:
            id_prestamo = prestamo_opciones[prestamo_sel]
            mostrar_formulario_pagos(id_prestamo)
            mostrar_historial_pagos(id_prestamo)
    else:
        st.info("No hay préstamos disponibles para registrar pagos.")


# =====================================================
#   FORMULARIO MEJORADO DE PAGOS
# =====================================================
def mostrar_formulario_pagos(id_prestamo):

    # Obtener información actual del préstamo
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT monto, interes_total, saldo_pendiente, estado
        FROM prestamos 
        WHERE id_prestamo = %s
    """, (id_prestamo,))
    prestamo_info = cursor.fetchone()
    con.close()

    if not prestamo_info:
        st.error("❌ No se encontró información del préstamo")
        return

    monto_original, interes_total, saldo_pendiente, estado = prestamo_info
    monto_total_original = monto_original + interes_total

    # Mostrar información del préstamo
    st.info(f"""
    **Información del Préstamo:**
    - 💰 Capital original: ${monto_original:,.2f}
    - 📈 Interés total: ${interes_total:,.2f}
    - 💵 Total original: ${monto_total_original:,.2f}
    - 🏦 Saldo pendiente: **${saldo_pendiente:,.2f}**
    - 📊 Estado: {estado.title()}
    """)

    # Si el préstamo ya está pagado, no mostrar formulario
    if saldo_pendiente <= 0:
        st.success("🎉 ¡Este préstamo ha sido completamente pagado!")
        return

    with st.form(f"form_pago_{id_prestamo}"):
        st.markdown("#### 💸 Nuevo Pago")

        # Calcular próximo número de pago automáticamente
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT COALESCE(MAX(numero_pago), 0) + 1 
            FROM prestamo_pagos 
            WHERE id_prestamo = %s
        """, (id_prestamo,))
        proximo_pago = cursor.fetchone()[0]
        con.close()

        numero_pago = st.number_input("Número de pago", min_value=1, value=proximo_pago, step=1)
        fecha_pago = st.date_input("Fecha del pago", datetime.date.today())
        
        # Mostrar monto máximo que se puede pagar
        st.write(f"**Monto máximo disponible para pago: ${saldo_pendiente:,.2f}**")
        capital = st.number_input("Monto del pago", min_value=0.01, max_value=float(saldo_pendiente), step=0.01)

        estado_pago = st.selectbox("Estado del pago", ["Pagado", "Pendiente"])

        guardar = st.form_submit_button("💾 Registrar Pago")

    if guardar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            # Calcular nuevo saldo
            nuevo_saldo = saldo_pendiente - capital
            
            # Verificar que no se pague más de lo debido
            if capital > saldo_pendiente:
                st.error("❌ El monto del pago no puede ser mayor al saldo pendiente")
                return

            # Registrar el pago
            cursor.execute("""
                INSERT INTO prestamo_pagos (id_prestamo, numero_pago, fecha, capital, estado)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                id_prestamo,
                numero_pago,
                fecha_pago,
                capital,
                estado_pago.lower()
            ))

            # Actualizar saldo pendiente del préstamo
            cursor.execute("""
                UPDATE prestamos 
                SET saldo_pendiente = %s,
                    estado = CASE 
                        WHEN %s <= 0 THEN 'finalizado' 
                        ELSE estado 
                    END
                WHERE id_prestamo = %s
            """, (nuevo_saldo, nuevo_saldo, id_prestamo))

            con.commit()
            st.success(f"✅ Pago registrado correctamente")
            st.info(f"💰 Nuevo saldo pendiente: ${nuevo_saldo:,.2f}")
            
            if nuevo_saldo <= 0:
                st.balloons()
                st.success("🎉 ¡Felicidades! El préstamo ha sido completamente pagado")
            
            time.sleep(2)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar pago: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'con' in locals() and con.is_connected():
                con.close()


# =====================================================
#   HISTORIAL DE PAGOS
# =====================================================
def mostrar_historial_pagos(id_prestamo):
    
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT 
            numero_pago,
            fecha,
            capital,
            estado,
            fecha_registro
        FROM prestamo_pagos 
        WHERE id_prestamo = %s 
        ORDER BY numero_pago
    """, (id_prestamo,))
    
    pagos = cursor.fetchall()
    con.close()

    if pagos:
        st.subheader("📋 Historial de Pagos")
        
        df_pagos = pd.DataFrame(pagos, columns=[
            "N° Pago", "Fecha", "Monto", "Estado", "Fecha Registro"
        ])
        
        # Formatear columnas
        df_pagos["Monto"] = df_pagos["Monto"].apply(lambda x: f"${x:,.2f}")
        df_pagos["Estado"] = df_pagos["Estado"].apply(lambda x: x.title())
        
        st.dataframe(df_pagos, use_container_width=True)
        
        # Resumen de pagos
        total_pagado = sum(p[2] for p in pagos)
        pagos_realizados = len(pagos)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 Total Pagado", f"${total_pagado:,.2f}")
        with col2:
            st.metric("📊 Pagos Realizados", pagos_realizados)
    else:
        st.info("ℹ️ No se han registrado pagos para este préstamo.")
