import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import datetime
import time
from decimal import Decimal

# =====================================================
#   FUNCIÓN CORREGIDA PARA OBTENER SALDO NETO DISPONIBLE
# =====================================================
def obtener_saldo_disponible_caja(id_grupo, fecha_consulta=None):
    """
    Obtiene el saldo neto acumulado en caja hasta una fecha específica
    """
    if fecha_consulta is None:
        fecha_consulta = datetime.date.today()
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        # Obtener TODAS las entradas de dinero acumuladas hasta la fecha de consulta
        cursor.execute("""
            SELECT COALESCE(SUM(MT.monto_a_pagar), 0) as total_multas
            FROM Multas MT
            JOIN Miembros M ON MT.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            AND MT.fecha <= %s
            AND MT.pagada = 1
        """, (id_grupo, fecha_consulta))
        total_multas_result = cursor.fetchone()[0]
        total_multas = float(total_multas_result) if total_multas_result else 0.0

        # Obtener TODOS los ahorros acumulados hasta la fecha
        cursor.execute("""
            SELECT 
                COALESCE(SUM(ahorros), 0) as total_ahorros,
                COALESCE(SUM(actividades), 0) as total_actividades,
                COALESCE(SUM(retiros), 0) as total_retiros
            FROM ahorro_final 
            WHERE id_grupo = %s AND fecha_registro <= %s
        """, (id_grupo, fecha_consulta))
        ahorros_data = cursor.fetchone()
        total_ahorros = float(ahorros_data[0]) if ahorros_data[0] else 0.0
        total_actividades = float(ahorros_data[1]) if ahorros_data[1] else 0.0
        total_retiros = float(ahorros_data[2]) if ahorros_data[2] else 0.0

        # Obtener TODOS los pagos de préstamos acumulados hasta la fecha
        cursor.execute("""
            SELECT COALESCE(SUM(PP.capital + PP.interes), 0) as total_pagos
            FROM prestamo_pagos PP
            JOIN prestamos P ON PP.id_prestamo = P.id_prestamo
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s 
            AND PP.fecha <= %s
            AND PP.estado = 'pagado'
        """, (id_grupo, fecha_consulta))
        total_pago_prestamos_result = cursor.fetchone()[0]
        total_pago_prestamos = float(total_pago_prestamos_result) if total_pago_prestamos_result else 0.0

        # Obtener TODOS los desembolsos de préstamos acumulados hasta la fecha
        cursor.execute("""
            SELECT COALESCE(SUM(P.monto), 0) as total_desembolsos
            FROM prestamos P
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s 
            AND P.fecha_desembolso <= %s
        """, (id_grupo, fecha_consulta))
        total_desembolsos_result = cursor.fetchone()[0]
        total_desembolsos = float(total_desembolsos_result) if total_desembolsos_result else 0.0

        con.close()

        # Calcular saldo neto acumulado
        total_entradas = total_multas + total_ahorros + total_actividades + total_pago_prestamos
        total_salidas = total_retiros + total_desembolsos
        saldo_neto = total_entradas - total_salidas

        return max(0.0, saldo_neto)  # No permitir saldos negativos

    except Exception as e:
        st.error(f"❌ Error al calcular saldo disponible: {str(e)}")
        return 0.0

# =====================================================
#   MÓDULO PRINCIPAL DE PRÉSTAMOS - COMPLETO
# =====================================================
def prestamos_modulo():
    # --------------------------------------
    # Validar sesión y grupo
    # --------------------------------------
    if "id_grupo" not in st.session_state or st.session_state.get("id_grupo") is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        
        # Botón para regresar al menú
        if st.button("⬅️ Regresar al Menú"):
            st.session_state.page = "menu"
            st.rerun()
        return

    id_grupo = st.session_state["id_grupo"]

    # TÍTULO
    st.markdown("<h1 style='text-align:center;'>💲 Gestión de Préstamos</h1>", unsafe_allow_html=True)

    # --------------------------------------
    # Obtener nombre del grupo
    # --------------------------------------
    try:
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
    except Exception as e:
        st.error(f"❌ Error al obtener información del grupo: {str(e)}")
        return

    # --------------------------------------
    # Obtener valores del reglamento - CORREGIDO
    # --------------------------------------
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT interes_por_10, max_prestamo, max_plazo
            FROM Reglamento
            WHERE id_grupo = %s
            LIMIT 1
        """, (id_grupo,))
        reglamento = cursor.fetchone()
        con.close()

        if reglamento:
            # Solo el interés se convierte a número para cálculos
            interes_por_10 = float(reglamento[0]) if reglamento[0] is not None else 0.0
            
            # Monto y plazo se mantienen como texto (sin conversión)
            monto_maximo_texto = str(reglamento[1]) if reglamento[1] is not None else "No definido"
            plazo_maximo_texto = str(reglamento[2]) if reglamento[2] is not None else "No definido"
            
            st.info(f"📊 Reglamento cargado: Interés {interes_por_10}% sobre el monto total")
        else:
            st.warning("⚠️ No se encontró reglamento para este grupo. Se usarán valores por defecto.")
            interes_por_10 = 0.0
            monto_maximo_texto = "No definido"
            plazo_maximo_texto = "No definido"
            
    except Exception as e:
        st.error(f"❌ Error al obtener reglamento: {str(e)}")
        interes_por_10 = 0.0
        monto_maximo_texto = "No definido"
        plazo_maximo_texto = "No definido"

    # --------------------------------------
    # Obtener miembros del grupo
    # --------------------------------------
    try:
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
            
            # Botón para regresar al menú
            if st.button("⬅️ Regresar al Menú"):
                st.session_state.page = "menu"
                st.rerun()
            return

        miembros_dict = {m[1]: m[0] for m in miembros}
        
    except Exception as e:
        st.error(f"❌ Error al obtener miembros: {str(e)}")
        return

    # =====================================================
    #   FORMULARIO: REGISTRAR NUEVO PRÉSTAMO - CON VALIDACIÓN DE CAJA
    # =====================================================
    with st.form("form_nuevo_prestamo"):
        st.subheader("📄 Nuevo Préstamo")

        miembro_seleccionado = st.selectbox("Selecciona un miembro", list(miembros_dict.keys()))
        proposito = st.text_input("Propósito del préstamo")
        
        fecha_desembolso = st.date_input("Fecha de desembolso", datetime.date.today())
        
        # OBTENER SALDO NETO DISPONIBLE EN CAJA PARA LA FECHA DE DESEMBOLSO
        saldo_disponible = obtener_saldo_disponible_caja(id_grupo, fecha_desembolso)
        
        # Mostrar información del saldo neto disponible
        st.info(f"💰 **Saldo neto disponible en caja:** ${saldo_disponible:,.2f}")
        
        # MONTO CON LÍMITE BASADO EN EL SALDO DISPONIBLE
        monto_maximo_permitido = float(saldo_disponible) if saldo_disponible > 0 else 0.01
        
        monto = st.number_input(
            "Monto del préstamo", 
            min_value=0.01, 
            max_value=monto_maximo_permitido,
            step=0.01,
            help=f"Monto máximo según reglamento: {monto_maximo_texto} | Saldo neto disponible: ${saldo_disponible:,.2f}"
        )
        
        fecha_vencimiento = st.date_input("Fecha de vencimiento", min_value=fecha_desembolso)

        # ⚠️ CAMPOS DE REGLAMENTO - SOLO LECTURA
        st.markdown("**Configuración del Reglamento:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input(
                "Interés sobre el monto total (%)",
                value=interes_por_10,
                step=0.01,
                disabled=True,
                key="interes_reglamento"
            )
        with col2:
            # Mostrar monto máximo como texto
            st.text_input(
                "Monto máximo permitido",
                value=monto_maximo_texto,
                disabled=True,
                key="monto_maximo_reglamento"
            )
        with col3:
            # Mostrar plazo máximo como texto
            st.text_input(
                "Plazo máximo",
                value=plazo_maximo_texto,
                disabled=True,
                key="plazo_maximo_reglamento"
            )

        # CALCULAR INTERÉS CORREGIDO - PORCENTAJE SOBRE EL MONTO TOTAL
        interes_total = (monto * interes_por_10) / 100
        monto_total = monto + interes_total

        enviar = st.form_submit_button("💾 Guardar Préstamo")

    # BOTÓN REGRESAR - FUERA DEL FORMULARIO
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
    st.write("---")

    if enviar:
        # VALIDACIONES MANUALES
        validacion_ok = True
        
        # 1. Validar monto máximo del reglamento (si es numérico)
        try:
            if monto_maximo_texto.replace('.', '').replace(',', '').isdigit():
                monto_maximo_num = float(monto_maximo_texto)
                if monto > monto_maximo_num:
                    st.error(f"❌ El monto no puede exceder el límite máximo del reglamento: {monto_maximo_texto}")
                    validacion_ok = False
        except:
            pass  # Si no es numérico, no validar
        
        # 2. Validar saldo disponible en caja
        if monto > saldo_disponible:
            st.error(f"❌ Fondos insuficientes. El monto solicitado (${monto:,.2f}) excede el saldo neto disponible en caja (${saldo_disponible:,.2f})")
            validacion_ok = False
        
        # 3. Validar que haya saldo disponible
        if saldo_disponible <= 0:
            st.error("❌ No hay saldo neto disponible en caja para realizar préstamos")
            validacion_ok = False

        if validacion_ok:
            try:
                con = obtener_conexion()
                cursor = con.cursor()

                # INSERT del préstamo - automáticamente como "activo"
                cursor.execute("""
                    INSERT INTO prestamos (id_miembro, proposito, monto, fecha_desembolso, 
                                         fecha_vencimiento, estado, interes_total)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    miembros_dict[miembro_seleccionado],
                    proposito,
                    monto,
                    fecha_desembolso,
                    fecha_vencimiento,
                    "activo",  # Estado fijo como "activo"
                    interes_total
                ))

                con.commit()
                st.success("✅ Préstamo registrado correctamente")
                st.info(f"💰 Total a pagar: ${monto_total:,.2f} (Capital: ${monto:,.2f} + Interés: ${interes_total:,.2f})")
                
                # Mostrar nuevo saldo disponible después del préstamo
                nuevo_saldo = saldo_disponible - monto
                st.info(f"💰 **Nuevo saldo neto disponible en caja:** ${nuevo_saldo:,.2f}")
                
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
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # PRIMERO: Obtener solo los préstamos básicos
        cursor.execute("""
            SELECT 
                P.id_prestamo, 
                M.nombre, 
                P.proposito, 
                P.monto,
                P.fecha_desembolso, 
                P.fecha_vencimiento, 
                P.estado, 
                P.interes_total
            FROM prestamos P
            JOIN Miembros M ON M.id_miembro = P.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY P.id_prestamo DESC, P.estado
        """, (id_grupo,))

        prestamos_basicos = cursor.fetchall()

        if not prestamos_basicos:
            st.info("No hay préstamos registrados en este grupo.")
            return

        # SEGUNDO: Para cada préstamo, calcular los pagos por separado
        prestamos_con_info = []
        for prestamo in prestamos_basicos:
            id_prestamo = prestamo[0]
            
            # CORRECCIÓN: Sumar capital + interés para el total pagado
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(capital + interes), 0) as total_pagado,
                    COUNT(id_pago) as numero_pagos
                FROM prestamo_pagos 
                WHERE id_prestamo = %s
            """, (id_prestamo,))
            
            info_pagos = cursor.fetchone()
            total_pagado = float(info_pagos[0]) if info_pagos[0] else 0
            numero_pagos = info_pagos[1] if info_pagos else 0
            
            # Calcular saldo pendiente CORRECTAMENTE
            monto_prestamo = float(prestamo[3]) if prestamo[3] else 0
            interes_total_prestamo = float(prestamo[7]) if prestamo[7] else 0
            monto_total = monto_prestamo + interes_total_prestamo
            saldo_pendiente = monto_total - total_pagado
            
            prestamos_con_info.append(prestamo + (total_pagado, numero_pagos, saldo_pendiente))

        con.close()

        # Tabla detallada de préstamos
        st.subheader("📋 Detalle de Préstamos")
        
        df = pd.DataFrame(prestamos_con_info, columns=[
            "ID", "Miembro", "Propósito", "Monto", "Fecha Desembolso", 
            "Fecha Vencimiento", "Estado", "Interés Total", "Total Pagado", 
            "Número de Pagos", "Saldo Pendiente"
        ])

        # Formatear columnas monetarias
        df["Monto"] = df["Monto"].apply(lambda x: f"${float(x):,.2f}" if x else "$0.00")
        df["Interés Total"] = df["Interés Total"].apply(lambda x: f"${float(x):,.2f}" if x else "$0.00")
        df["Saldo Pendiente"] = df["Saldo Pendiente"].apply(lambda x: f"${float(x):,.2f}" if x else "$0.00")
        df["Total Pagado"] = df["Total Pagado"].apply(lambda x: f"${float(x):,.2f}" if x else "$0.00")

        st.dataframe(df, use_container_width=True)

        # Selección de préstamo para pagos
        st.subheader("💳 Registrar Pago")
        
        prestamo_opciones = {}
        for row in prestamos_con_info:
            total_pagado = row[8]
            saldo_pendiente = row[10]
            
            texto_opcion = f"{row[1]} - ${saldo_pendiente:,.2f} pendientes (Pagado: ${total_pagado:,.2f})"
            prestamo_opciones[texto_opcion] = row[0]
            
        if prestamo_opciones:
            prestamo_sel = st.selectbox("Selecciona un préstamo:", list(prestamo_opciones.keys()))
            
            if prestamo_sel:
                id_prestamo = prestamo_opciones[prestamo_sel]
                mostrar_formulario_pagos(id_prestamo)
                mostrar_historial_pagos(id_prestamo)
        else:
            st.info("No hay préstamos disponibles para registrar pagos.")

    except Exception as e:
        st.error(f"❌ Error al cargar la lista de préstamos: {str(e)}")


# =====================================================
#   FORMULARIO MEJORADO DE PAGOS - UNIFICADO (CORREGIDO)
# =====================================================
def mostrar_formulario_pagos(id_prestamo):
    try:
        # Obtener información actual del préstamo
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT monto, interes_total, estado
            FROM prestamos 
            WHERE id_prestamo = %s
        """, (id_prestamo,))
        prestamo_info = cursor.fetchone()
        
        if not prestamo_info:
            st.error("❌ No se encontró información del préstamo")
            return

        # CORRECCIÓN: Sumar capital + interés para el total pagado
        cursor.execute("""
            SELECT COALESCE(SUM(capital + interes), 0) 
            FROM prestamo_pagos 
            WHERE id_prestamo = %s
        """, (id_prestamo,))
        total_pagado_result = cursor.fetchone()[0]
        con.close()

        # CONVERTIR TODOS LOS VALORES A FLOAT PARA EVITAR ERRORES DE TIPO
        monto_original = float(prestamo_info[0]) if prestamo_info[0] is not None else 0.0
        interes_total = float(prestamo_info[1]) if prestamo_info[1] is not None else 0.0
        estado = prestamo_info[2]
        total_pagado = float(total_pagado_result) if total_pagado_result is not None else 0.0

        monto_total_original = monto_original + interes_total
        saldo_pendiente = monto_total_original - total_pagado

        # Mostrar información del préstamo
        st.info(f"""
        **Información del Préstamo:**
        - 💰 Capital original: ${monto_original:,.2f}
        - 📈 Interés total: ${interes_total:,.2f}
        - 💵 Total original: ${monto_total_original:,.2f}
        - ✅ Total pagado: ${total_pagado:,.2f}
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

            # CORREGIDO: Campo de solo lectura para el número de pago
            st.text_input("Número de pago", value=proximo_pago, disabled=True, key=f"num_pago_{id_prestamo}")
            # Mantener el valor en una variable para usarlo en el INSERT
            numero_pago = proximo_pago
            
            fecha_pago = st.date_input("Fecha del pago", datetime.date.today())
            
            # CAMPO UNIFICADO - SOLO MONTO
            st.write(f"**Monto máximo disponible para pago: ${saldo_pendiente:,.2f}**")
            
            # ÚNICO CAMPO DE MONTO - lo que se pague se abona al total
            monto_pago = st.number_input(
                "Monto del pago", 
                min_value=0.01, 
                max_value=float(saldo_pendiente), 
                step=0.01,
                help="El monto que pagues se abonará directamente al total que debes"
            )

            guardar = st.form_submit_button("💾 Registrar Pago")

        if guardar:
            try:
                con = obtener_conexion()
                cursor = con.cursor()

                # Verificar que no se pague más de lo debido
                if float(monto_pago) > saldo_pendiente:
                    st.error("❌ El monto del pago no puede ser mayor al saldo pendiente")
                    return

                # DISTRIBUCIÓN AUTOMÁTICA: Primero se abona al capital, luego al interés
                # Calcular cuánto capital queda por pagar
                capital_pendiente = monto_original - total_pagado
                
                if float(monto_pago) <= capital_pendiente:
                    # Todo el pago va al capital
                    capital_abonado = float(monto_pago)
                    interes_abonado = 0.00
                else:
                    # Se paga todo el capital pendiente y el resto va al interés
                    capital_abonado = capital_pendiente
                    interes_abonado = float(monto_pago) - capital_pendiente

                # Registrar el pago con estado automáticamente como "pagado"
                cursor.execute("""
                    INSERT INTO prestamo_pagos (id_prestamo, numero_pago, fecha, capital, interes, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_prestamo,
                    numero_pago,
                    fecha_pago,
                    capital_abonado,
                    interes_abonado,
                    "pagado"  # ESTADO FIJO COMO "pagado"
                ))

                # Calcular nuevo total pagado
                nuevo_total_pagado = total_pagado + float(monto_pago)
                
                # Verificar si el préstamo queda completamente pagado
                if nuevo_total_pagado >= monto_total_original:
                    cursor.execute("""
                        UPDATE prestamos 
                        SET estado = 'finalizado'
                        WHERE id_prestamo = %s
                    """, (id_prestamo,))
                else:
                    # Si no está completamente pagado, mantener como activo
                    cursor.execute("""
                        UPDATE prestamos 
                        SET estado = 'activo'
                        WHERE id_prestamo = %s
                    """, (id_prestamo,))

                con.commit()
                st.success(f"✅ Pago registrado correctamente")
                
                # Mostrar desglose del pago
                st.info(f"""
                **Desglose del pago:**
                - 💰 Capital abonado: ${capital_abonado:,.2f}
                - 🏦 Nuevo saldo pendiente: **${saldo_pendiente - float(monto_pago):,.2f}**
                """)
                
                if (saldo_pendiente - float(monto_pago)) <= 0:
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

    except Exception as e:
        st.error(f"❌ Error al cargar formulario de pagos: {str(e)}")


# =====================================================
#   HISTORIAL DE PAGOS - SIN COLUMNA DE INTERÉS
# =====================================================
def mostrar_historial_pagos(id_prestamo):
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        # Consulta con los nombres exactos de tus columnas
        cursor.execute("""
            SELECT 
                id_pago,
                numero_pago, 
                fecha,
                capital,
                interes,
                estado
            FROM prestamo_pagos 
            WHERE id_prestamo = %s 
            ORDER BY numero_pago
        """, (id_prestamo,))
        
        pagos = cursor.fetchall()
        con.close()

        if pagos:
            st.subheader("📋 Historial de Pagos")
            
            # Crear DataFrame con los nombres exactos
            df_pagos = pd.DataFrame(pagos, columns=[
                "ID Pago", "N° Pago", "Fecha", "Capital", "Interés", "Estado"
            ])
            
            # Calcular el monto total de cada pago (capital + interés)
            montos_totales = []
            for pago in pagos:
                capital = float(pago[3]) if pago[3] is not None else 0.0
                interes = float(pago[4]) if pago[4] is not None else 0.0
                monto_total = capital + interes
                montos_totales.append(monto_total)
            
            # Agregar columna de monto total al DataFrame
            df_pagos["Monto Total"] = montos_totales
            
            # Formatear columnas
            df_pagos["Monto Total"] = df_pagos["Monto Total"].apply(lambda x: f"${x:,.2f}")
            df_pagos["Estado"] = df_pagos["Estado"].apply(lambda x: x.title() if x else "N/A")
            
            # Mostrar solo las columnas relevantes (SIN INTERÉS)
            columnas_mostrar = ["N° Pago", "Fecha", "Monto Total", "Estado"]
            st.dataframe(df_pagos[columnas_mostrar], use_container_width=True)
            
            # Resumen de pagos - SOLO MONTO TOTAL
            total_capital_pagado = sum(float(p[3]) if p[3] is not None else 0.0 for p in pagos)
            total_interes_pagado = sum(float(p[4]) if p[4] is not None else 0.0 for p in pagos)
            total_pagado = total_capital_pagado + total_interes_pagado
            pagos_realizados = len(pagos)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Total Pagado", f"${total_pagado:,.2f}")
            with col2:
                st.metric("📊 Total Pagos", pagos_realizados)
            with col3:
                # Calcular porcentaje pagado si hay información del préstamo
                try:
                    con = obtener_conexion()
                    cursor = con.cursor()
                    cursor.execute("""
                        SELECT monto, interes_total 
                        FROM prestamos 
                        WHERE id_prestamo = %s
                    """, (id_prestamo,))
                    prestamo_info = cursor.fetchone()
                    con.close()
                    
                    if prestamo_info:
                        monto_original = float(prestamo_info[0]) if prestamo_info[0] is not None else 0.0
                        interes_total = float(prestamo_info[1]) if prestamo_info[1] is not None else 0.0
                        monto_total_prestamo = monto_original + interes_total
                        
                        if monto_total_prestamo > 0:
                            porcentaje_pagado = (total_pagado / monto_total_prestamo) * 100
                            st.metric("📈 % Pagado", f"{porcentaje_pagado:.1f}%")
                        else:
                            st.metric("📈 % Pagado", "0%")
                    else:
                        st.metric("📈 % Pagado", "N/A")
                except:
                    st.metric("📈 % Pagado", "N/A")
                
        else:
            st.info("ℹ️ No se han registrado pagos para este préstamo.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar el historial de pagos: {str(e)}")

