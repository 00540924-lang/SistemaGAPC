import streamlit as st 
import mysql.connector
from datetime import date
from modulos.config.conexion import obtener_conexion
import pandas as pd
import matplotlib.pyplot as plt

def obtener_datos_ahorro_automaticos(id_grupo, fecha):
    """
    Obtiene automáticamente los datos de ahorro del módulo de ahorro
    para una fecha y grupo específicos
    """
    conn = obtener_conexion()
    if not conn:
        return 0.0, 0.0, 0.0
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # Obtener la suma de ahorros, actividades y retiros del módulo de ahorro
        cursor.execute("""
            SELECT 
                COALESCE(SUM(ahorros), 0) as total_ahorros,
                COALESCE(SUM(actividades), 0) as total_actividades,
                COALESCE(SUM(retiros), 0) as total_retiros
            FROM ahorro_final 
            WHERE id_grupo = %s AND fecha_registro = %s
        """, (id_grupo, fecha))
        
        resultado = cursor.fetchone()
        
        # Asegurarse de que no hay más resultados
        cursor.fetchall()
        
        if resultado:
            return (
                float(resultado['total_ahorros']),
                float(resultado['total_actividades']),
                float(resultado['total_retiros'])
            )
        return 0.0, 0.0, 0.0
        
    except Exception as e:
        st.error(f"Error al obtener datos automáticos de ahorro: {e}")
        return 0.0, 0.0, 0.0
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_multas_automaticas(id_grupo, fecha):
    """Obtiene las multas pagadas automáticamente"""
    conn = obtener_conexion()
    if not conn:
        return 0.0
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
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
        
        # Asegurarse de que no hay más resultados
        cursor.fetchall()
        
        return float(resultado_multa["total_multas"]) if resultado_multa else 0.0
        
    except Exception as e:
        st.error(f"Error al obtener multas automáticas: {e}")
        return 0.0
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def manejar_registro_caja(id_grupo, fecha, datos):
    """Maneja la creación o actualización de registros de caja en una sola conexión"""
    conn = obtener_conexion()
    if not conn:
        return False, "Error de conexión"
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # PRIMERO: Verificar si existe un registro
        cursor.execute("SELECT id_caja FROM Caja WHERE id_grupo = %s AND fecha = %s", (id_grupo, fecha))
        registro_existente = cursor.fetchone()
        
        # Asegurarse de que no hay más resultados
        cursor.fetchall()
        
        if registro_existente:
            # SEGUNDO: Actualizar registro existente
            cursor.execute("""
                UPDATE Caja SET
                    multas = %s,
                    ahorros = %s,
                    otras_actividades = %s,
                    pago_prestamos = %s,
                    otros_ingresos = %s,
                    total_entrada = %s,
                    retiro_ahorros = %s,
                    desembolso = %s,
                    gastos_grupo = %s,
                    total_salida = %s,
                    saldo_cierre = %s
                WHERE id_caja = %s
            """, (
                datos['multas'],
                datos['ahorros'],
                datos['otras_actividades'],
                datos['pago_prestamos'],
                datos['otros_ingresos'],
                datos['total_entrada'],
                datos['retiro_ahorros'],
                datos['desembolso'],
                datos['gastos_grupo'],
                datos['total_salida'],
                datos['saldo_cierre'],
                registro_existente['id_caja']
            ))
            conn.commit()
            return True, f"Registro actualizado correctamente (ID: {registro_existente['id_caja']})"
        else:
            # SEGUNDO: Crear nuevo registro
            cursor.execute("""
                INSERT INTO Caja (
                    id_grupo, fecha, multas, ahorros, otras_actividades, 
                    pago_prestamos, otros_ingresos, total_entrada,
                    retiro_ahorros, desembolso, gastos_grupo, total_salida,
                    saldo_cierre
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                datos['id_grupo'],
                datos['fecha'],
                datos['multas'],
                datos['ahorros'],
                datos['otras_actividades'],
                datos['pago_prestamos'],
                datos['otros_ingresos'],
                datos['total_entrada'],
                datos['retiro_ahorros'],
                datos['desembolso'],
                datos['gastos_grupo'],
                datos['total_salida'],
                datos['saldo_cierre']
            ))
            conn.commit()
            return True, "Nuevo registro creado correctamente"
            
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error en la base de datos: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_historial_caja(id_grupo, fecha_inicio=None, fecha_fin=None):
    """Obtiene el historial de caja con filtros opcionales"""
    conn = obtener_conexion()
    if not conn:
        return []
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        query = "SELECT fecha, total_entrada, total_salida FROM Caja WHERE id_grupo = %s"
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
        
        # Asegurarse de que no hay más resultados
        cursor.fetchall()
        
        return registros
            
    except Exception as e:
        st.error(f"Error al obtener historial: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def mostrar_caja(id_grupo):
    """
    Módulo de caja con gráfico de historial.
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
    # 1. Fecha
    # ===============================
    fecha = st.date_input("📅 Fecha de registro", date.today())
    
    # ===============================
    # 2. OBTENER DATOS AUTOMÁTICOS
    # ===============================
    ahorros_auto, actividades_auto, retiros_auto = obtener_datos_ahorro_automaticos(id_grupo, fecha)
    multa_auto = obtener_multas_automaticas(id_grupo, fecha)

    # ===============================
    # 3. DINERO QUE ENTRA - CON MÉTRICAS GRANDES
    # ===============================
    st.subheader("🟩 Dinero que entra")
    
    # Valores fijos (puedes cambiar estos según necesites)
    pagos_prestamos = 0.0
    otros_ingresos = 0.0
    
    # Calcular total entrada
    total_entrada = multa_auto + ahorros_auto + actividades_auto + pagos_prestamos + otros_ingresos
    
    # Primera fila de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Multas PAGADAS del día", 
            f"${multa_auto:,.2f}",
            help="Valor automático de multas pagadas"
        )
    
    with col2:
        st.metric(
            "Ahorros", 
            f"${ahorros_auto:,.2f}",
            help="Valor automático del módulo de ahorro"
        )
    
    with col3:
        st.metric(
            "Otras actividades", 
            f"${actividades_auto:,.2f}",
            help="Valor automático del módulo de ahorro"
        )
    
    with col4:
        st.metric(
            "Pago de préstamos", 
            f"${pagos_prestamos:,.2f}",
            help="Capital e interés"
        )

    # Segunda fila de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Otros ingresos del grupo", 
            f"${otros_ingresos:,.2f}"
        )
    
    with col2:
        # Espacio vacío para alineación
        st.write("")
    
    with col3:
        # Espacio vacío para alineación
        st.write("")
    
    with col4:
        # Mostrar total entrada como métrica grande
        st.metric(
            "🔹 Total dinero que entra", 
            f"${total_entrada:,.2f}",
            delta=None
        )

    st.write("---")

    # ===============================
    # 4. DINERO QUE SALE - CON MÉTRICAS GRANDES
    # ===============================
    st.subheader("🟥 Dinero que sale")
    
    # Valores fijos (puedes cambiar estos según necesites)
    desembolso = 0.0
    gastos_grupo = 0.0
    
    # Calcular total salida
    total_salida = retiros_auto + desembolso + gastos_grupo
    
    # Fila de métricas para dinero que sale
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Retiros de ahorros", 
            f"${retiros_auto:,.2f}",
            help="Valor automático del módulo de ahorro"
        )
    
    with col2:
        st.metric(
            "Desembolso de préstamos", 
            f"${desembolso:,.2f}"
        )
    
    with col3:
        st.metric(
            "Otros gastos del grupo", 
            f"${gastos_grupo:,.2f}"
        )
    
    with col4:
        # Mostrar total salida como métrica grande
        st.metric(
            "🔻 Total dinero que sale", 
            f"${total_salida:,.2f}",
            delta=None
        )

    st.write("---")

    # ===============================
    # 5. SALDO NETO - CON MÉTRICA GRANDE
    # ===============================
    st.subheader("⚖️ Saldo del cierre")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        saldo_neto = total_entrada - total_salida
        st.metric(
            "Saldo neto", 
            f"${saldo_neto:,.2f}",
            delta=None
        )

    # ===============================
    # 6. GUARDADO INTELIGENTE (ACTUALIZAR O CREAR)
    # ===============================
    if total_entrada > 0 or total_salida > 0:
        # Preparar los datos para guardar
        datos_caja = {
            'id_grupo': id_grupo,
            'fecha': fecha,
            'multas': multa_auto,
            'ahorros': ahorros_auto,
            'otras_actividades': actividades_auto,
            'pago_prestamos': pagos_prestamos,
            'otros_ingresos': otros_ingresos,
            'total_entrada': total_entrada,
            'retiro_ahorros': retiros_auto,
            'desembolso': desembolso,
            'gastos_grupo': gastos_grupo,
            'total_salida': total_salida,
            'saldo_cierre': saldo_neto
        }
        
        success, message = manejar_registro_caja(id_grupo, fecha, datos_caja)
        if success:
            st.success(f"✅ {message}")
        else:
            st.error(f"❌ {message}")

    # ===============================
    # 7. Historial con gráfico y filtros
    # ===============================
    st.write("---")
    st.subheader("📊 Historial de Caja")
    st.info("Filtre por fecha o deje vacío para ver todos los registros.")

    col1, col2, col3 = st.columns([1,1,1])
    fecha_inicio = col1.date_input("📅 Fecha inicio (opcional)", key="filtro_inicio")
    fecha_fin = col2.date_input("📅 Fecha fin (opcional)", key="filtro_fin")

    if col3.button("🧹 Limpiar filtros"):
        st.session_state["limpiar_filtros"] = True

    if st.session_state.get("limpiar_filtros", False):
        fecha_inicio = None
        fecha_fin = None
        st.session_state["limpiar_filtros"] = False

    # Obtener historial
    registros = obtener_historial_caja(id_grupo, fecha_inicio, fecha_fin)

    if registros:
        df = pd.DataFrame(registros)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha').reset_index(drop=True)

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
            <div style="text-align:left; font-size:16px; line-height:1.6;">
                <div style="color:#4CAF50;"><strong>Entrada total:</strong> ${df['total_entrada'].sum():.2f}</div>
                <div style="color:#F44336;"><strong>Salida total:</strong> ${df['total_salida'].sum():.2f}</div>
                <div style="color:#0000FF; font-size:18px;"><strong>💰 Saldo final: ${saldo_final:,.2f}</strong></div>
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.info("No hay registros para mostrar.")

    # ===============================
    # 8. Botón regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
