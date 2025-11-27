import streamlit as st
import mysql.connector
from datetime import date, datetime, timedelta
from modulos.config.conexion import obtener_conexion
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def obtener_multas_pagadas_rango(id_grupo, fecha_inicio, fecha_fin):
    """Obtiene las multas pagadas directamente de la tabla Multas - MISMAS FUNCIONES QUE CAJA"""
    conn = obtener_conexion()
    if not conn:
        return 0.0
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("""
            SELECT COALESCE(SUM(MT.monto_a_pagar), 0) AS total_multas
            FROM Multas MT
            JOIN Miembros M ON MT.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            AND MT.fecha BETWEEN %s AND %s
            AND MT.pagada = 1
        """, (id_grupo, fecha_inicio, fecha_fin))

        resultado_multa = cursor.fetchone()
        
        # Asegurarse de que no hay más resultados
        cursor.fetchall()
        
        return float(resultado_multa["total_multas"]) if resultado_multa else 0.0
        
    except Exception as e:
        st.error(f"Error al obtener multas pagadas: {e}")
        return 0.0
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_ahorros_rango(id_grupo, fecha_inicio, fecha_fin):
    """Obtiene los datos de ahorro directamente del módulo de ahorro - MISMAS FUNCIONES QUE CAJA"""
    conn = obtener_conexion()
    if not conn:
        return 0.0, 0.0, 0.0
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        cursor.execute("""
            SELECT 
                COALESCE(SUM(ahorros), 0) as total_ahorros,
                COALESCE(SUM(actividades), 0) as total_actividades,
                COALESCE(SUM(retiros), 0) as total_retiros
            FROM ahorro_final 
            WHERE id_grupo = %s AND fecha_registro BETWEEN %s AND %s
        """, (id_grupo, fecha_inicio, fecha_fin))
        
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
        st.error(f"Error al obtener datos de ahorro: {e}")
        return 0.0, 0.0, 0.0
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_prestamos_rango(id_grupo, fecha_inicio, fecha_fin):
    """Obtiene los datos de préstamos directamente de las tablas de préstamos - MISMAS FUNCIONES QUE CAJA"""
    conn = obtener_conexion()
    if not conn:
        return 0.0, 0.0
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # 1. Obtener pagos de préstamos
        cursor.execute("""
            SELECT COALESCE(SUM(PP.capital + PP.interes), 0) as total_pagos
            FROM prestamo_pagos PP
            JOIN prestamos P ON PP.id_prestamo = P.id_prestamo
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s 
            AND PP.fecha BETWEEN %s AND %s
            AND PP.estado = 'pagado'
        """, (id_grupo, fecha_inicio, fecha_fin))
        
        resultado_pagos = cursor.fetchone()
        total_pagos = float(resultado_pagos['total_pagos']) if resultado_pagos else 0.0
        
        # 2. Obtener desembolsos de préstamos - SIN FILTRO DE ESTADO
        cursor.execute("""
            SELECT COALESCE(SUM(P.monto), 0) as total_desembolsos
            FROM prestamos P
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s 
            AND P.fecha_desembolso BETWEEN %s AND %s
        """, (id_grupo, fecha_inicio, fecha_fin))
        
        resultado_desembolsos = cursor.fetchone()
        total_desembolsos = float(resultado_desembolsos['total_desembolsos']) if resultado_desembolsos else 0.0
        
        return total_pagos, total_desembolsos
        
    except Exception as e:
        st.error(f"Error al obtener datos de préstamos: {e}")
        return 0.0, 0.0
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_estadisticas_grupo(id_grupo, fecha_inicio=None, fecha_fin=None, id_miembro=None):
    """Obtiene estadísticas usando las MISMAS funciones que el módulo de caja"""
    
    # Si hay filtro de miembro, usar lógica diferente
    if id_miembro:
        return obtener_estadisticas_grupo_con_miembro(id_grupo, fecha_inicio, fecha_fin, id_miembro)
    
    # Obtener datos de cada módulo - EXACTAMENTE IGUAL QUE EN CAJA
    total_multas = obtener_multas_pagadas_rango(id_grupo, fecha_inicio, fecha_fin)
    total_ahorros, total_actividades, total_retiros = obtener_ahorros_rango(id_grupo, fecha_inicio, fecha_fin)
    total_pago_prestamos, total_desembolso = obtener_prestamos_rango(id_grupo, fecha_inicio, fecha_fin)
    
    # Valores por defecto para campos que no tenemos en otros módulos
    total_otros_ingresos = 0.0
    total_gastos_grupo = 0.0
    
    # Calcular totales - EXACTAMENTE IGUAL QUE EN CAJA
    total_entrada = total_multas + total_ahorros + total_actividades + total_pago_prestamos + total_otros_ingresos
    total_salida = total_retiros + total_desembolso + total_gastos_grupo
    total_saldo_cierre = total_entrada - total_salida
    
    # Obtener estadísticas adicionales para el dashboard
    conn = obtener_conexion()
    total_miembros = 0
    multas_pagadas_count = 0
    multas_pendientes_count = 0
    num_prestamos_activos = 0
    num_prestamos_pagados = 0
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Total de miembros
            cursor.execute("SELECT COUNT(*) as total FROM Grupomiembros WHERE id_grupo = %s", (id_grupo,))
            total_miembros = cursor.fetchone()['total']
            
            # Conteo de multas
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN MT.pagada = 1 THEN 1 END) as pagadas,
                    COUNT(CASE WHEN MT.pagada = 0 THEN 1 END) as pendientes
                FROM Multas MT
                JOIN Miembros M ON MT.id_miembro = M.id_miembro
                JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
                WHERE GM.id_grupo = %s AND MT.fecha BETWEEN %s AND %s
            """, (id_grupo, fecha_inicio, fecha_fin))
            multas_counts = cursor.fetchone()
            multas_pagadas_count = multas_counts['pagadas'] if multas_counts else 0
            multas_pendientes_count = multas_counts['pendientes'] if multas_counts else 0
            
            # Conteo de préstamos
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN P.estado = 'activo' THEN 1 END) as activos,
                    COUNT(CASE WHEN P.estado = 'pagado' THEN 1 END) as pagados
                FROM prestamos P
                JOIN Miembros M ON P.id_miembro = M.id_miembro
                JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
                WHERE GM.id_grupo = %s AND P.fecha_desembolso BETWEEN %s AND %s
            """, (id_grupo, fecha_inicio, fecha_fin))
            prestamos_counts = cursor.fetchone()
            num_prestamos_activos = prestamos_counts['activos'] if prestamos_counts else 0
            num_prestamos_pagados = prestamos_counts['pagados'] if prestamos_counts else 0
            
            cursor.close()
        except Exception as e:
            st.error(f"Error al obtener estadísticas adicionales: {e}")
        finally:
            if conn.is_connected():
                conn.close()
    
    # Porcentajes
    total_multas_count = multas_pagadas_count + multas_pendientes_count
    porcentaje_multas_pagadas = (multas_pagadas_count / total_multas_count * 100) if total_multas_count > 0 else 0
    
    total_prestamos_count = num_prestamos_activos + num_prestamos_pagados
    porcentaje_prestamos_pagados = (num_prestamos_pagados / total_prestamos_count * 100) if total_prestamos_count > 0 else 0
    
    return {
        # Totales principales (IGUAL QUE CAJA)
        'total_multas': total_multas,
        'total_ahorros': total_ahorros,
        'total_actividades': total_actividades,
        'total_pago_prestamos': total_pago_prestamos,
        'total_entrada': total_entrada,
        'total_retiros': total_retiros,
        'total_desembolso': total_desembolso,
        'total_salida': total_salida,
        'saldo_neto': total_saldo_cierre,  # Este es el saldo total correcto
        
        # Estadísticas adicionales para el dashboard
        'total_miembros': total_miembros,
        'multas_pagadas': multas_pagadas_count,
        'multas_pendientes': multas_pendientes_count,
        'porcentaje_multas_pagadas': porcentaje_multas_pagadas,
        'num_prestamos_activos': num_prestamos_activos,
        'num_prestamos_pagados': num_prestamos_pagados,
        'porcentaje_prestamos_pagados': porcentaje_prestamos_pagados
    }

def obtener_estadisticas_grupo_con_miembro(id_grupo, fecha_inicio, fecha_fin, id_miembro):
    """Obtiene estadísticas cuando hay filtro por miembro específico"""
    conn = obtener_conexion()
    if not conn:
        return {}
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Consulta para un miembro específico
        query = """
            SELECT 
                -- Multas pagadas del miembro
                COALESCE(SUM(CASE WHEN MT.pagada = 1 THEN MT.monto_a_pagar ELSE 0 END), 0) as total_multas,
                
                -- Ahorros del miembro
                COALESCE(SUM(AF.ahorros), 0) as total_ahorros,
                COALESCE(SUM(AF.actividades), 0) as total_actividades,
                COALESCE(SUM(AF.retiros), 0) as total_retiros,
                
                -- Pagos de préstamos del miembro
                COALESCE(SUM(PP.capital + PP.interes), 0) as total_pago_prestamos,
                
                -- Desembolsos de préstamos al miembro
                COALESCE(SUM(P.monto), 0) as total_desembolso,
                
                -- Conteos
                COUNT(DISTINCT CASE WHEN MT.pagada = 1 THEN MT.id_multa END) as multas_pagadas,
                COUNT(DISTINCT CASE WHEN MT.pagada = 0 THEN MT.id_multa END) as multas_pendientes,
                COUNT(DISTINCT CASE WHEN P.estado = 'activo' THEN P.id_prestamo END) as num_prestamos_activos,
                COUNT(DISTINCT CASE WHEN P.estado = 'pagado' THEN P.id_prestamo END) as num_prestamos_pagados
                
            FROM Miembros M
            JOIN Grupomiembros GM ON M.id_miembro = GM.id_miembro
            LEFT JOIN Multas MT ON M.id_miembro = MT.id_miembro AND MT.fecha BETWEEN %s AND %s
            LEFT JOIN ahorro_final AF ON M.id_miembro = AF.id_miembro AND AF.id_grupo = GM.id_grupo AND AF.fecha_registro BETWEEN %s AND %s
            LEFT JOIN prestamos P ON M.id_miembro = P.id_miembro AND P.fecha_desembolso BETWEEN %s AND %s
            LEFT JOIN prestamo_pagos PP ON P.id_prestamo = PP.id_prestamo AND PP.fecha BETWEEN %s AND %s AND PP.estado = 'pagado'
            WHERE GM.id_grupo = %s AND M.id_miembro = %s
        """
        
        params = [fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, id_grupo, id_miembro]
        cursor.execute(query, tuple(params))
        resultado = cursor.fetchone()
        
        if resultado:
            # Calcular totales (MISMA LÓGICA QUE CAJA)
            total_entrada = (
                resultado['total_multas'] + 
                resultado['total_ahorros'] + 
                resultado['total_actividades'] + 
                resultado['total_pago_prestamos']
            )
            total_salida = resultado['total_retiros'] + resultado['total_desembolso']
            saldo_neto = total_entrada - total_salida
            
            # Porcentajes
            total_multas_count = resultado['multas_pagadas'] + resultado['multas_pendientes']
            porcentaje_multas_pagadas = (resultado['multas_pagadas'] / total_multas_count * 100) if total_multas_count > 0 else 0
            
            total_prestamos_count = resultado['num_prestamos_activos'] + resultado['num_prestamos_pagados']
            porcentaje_prestamos_pagados = (resultado['num_prestamos_pagados'] / total_prestamos_count * 100) if total_prestamos_count > 0 else 0
            
            return {
                'total_multas': resultado['total_multas'],
                'total_ahorros': resultado['total_ahorros'],
                'total_actividades': resultado['total_actividades'],
                'total_pago_prestamos': resultado['total_pago_prestamos'],
                'total_entrada': total_entrada,
                'total_retiros': resultado['total_retiros'],
                'total_desembolso': resultado['total_desembolso'],
                'total_salida': total_salida,
                'saldo_neto': saldo_neto,
                'total_miembros': 1,  # Solo un miembro en el filtro
                'multas_pagadas': resultado['multas_pagadas'],
                'multas_pendientes': resultado['multas_pendientes'],
                'porcentaje_multas_pagadas': porcentaje_multas_pagadas,
                'num_prestamos_activos': resultado['num_prestamos_activos'],
                'num_prestamos_pagados': resultado['num_prestamos_pagados'],
                'porcentaje_prestamos_pagados': porcentaje_prestamos_pagados
            }
        
        return {}
        
    except Exception as e:
        st.error(f"Error al obtener estadísticas por miembro: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_estadisticas_por_miembro(id_grupo, fecha_inicio=None, fecha_fin=None):
    """Obtiene estadísticas detalladas por cada miembro del grupo"""
    conn = obtener_conexion()
    if not conn:
        return []
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                M.id_miembro,
                M.Nombre,
                
                -- Entradas del miembro
                COALESCE(SUM(CASE WHEN MT.pagada = 1 THEN MT.monto_a_pagar ELSE 0 END), 0) as total_multas,
                COALESCE(SUM(AF.ahorros), 0) as total_ahorros,
                COALESCE(SUM(AF.actividades), 0) as total_actividades,
                COALESCE(SUM(PP.capital + PP.interes), 0) as total_pago_prestamos,
                
                -- Salidas del miembro
                COALESCE(SUM(AF.retiros), 0) as total_retiros,
                COALESCE(SUM(P.monto), 0) as total_desembolso
                
            FROM Miembros M
            JOIN Grupomiembros GM ON M.id_miembro = GM.id_miembro
            LEFT JOIN Multas MT ON M.id_miembro = MT.id_miembro AND MT.fecha BETWEEN %s AND %s
            LEFT JOIN ahorro_final AF ON M.id_miembro = AF.id_miembro AND AF.id_grupo = GM.id_grupo AND AF.fecha_registro BETWEEN %s AND %s
            LEFT JOIN prestamos P ON M.id_miembro = P.id_miembro AND P.fecha_desembolso BETWEEN %s AND %s
            LEFT JOIN prestamo_pagos PP ON P.id_prestamo = PP.id_prestamo AND PP.fecha BETWEEN %s AND %s AND PP.estado = 'pagado'
            WHERE GM.id_grupo = %s
            GROUP BY M.id_miembro, M.Nombre
            ORDER BY total_ahorros DESC
        """
        
        params = [fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, id_grupo]
        cursor.execute(query, tuple(params))
        resultados = cursor.fetchall()
        
        # Calcular saldo para cada miembro (MISMA LÓGICA QUE CAJA)
        for miembro in resultados:
            total_entradas = (
                miembro['total_multas'] + 
                miembro['total_ahorros'] + 
                miembro['total_actividades'] + 
                miembro['total_pago_prestamos']
            )
            total_salidas = miembro['total_retiros'] + miembro['total_desembolso']
            miembro['saldo_ahorro'] = total_entradas - total_salidas
            miembro['total_entradas'] = total_entradas
            miembro['total_salidas'] = total_salidas
        
        return resultados
        
    except Exception as e:
        st.error(f"Error al obtener estadísticas por miembro: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Las funciones obtener_evolucion_ahorros y obtener_distribucion_por_tipo se mantienen igual
def obtener_evolucion_ahorros(id_grupo, fecha_inicio=None, fecha_fin=None, id_miembro=None):
    """Obtiene la evolución de ahorros en el tiempo"""
    conn = obtener_conexion()
    if not conn:
        return []
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        condiciones = ["AF.id_grupo = %s"]
        params = [id_grupo]
        
        if fecha_inicio and fecha_fin:
            condiciones.append("AF.fecha_registro BETWEEN %s AND %s")
            params.extend([fecha_inicio, fecha_fin])
        
        if id_miembro:
            condiciones.append("AF.id_miembro = %s")
            params.append(id_miembro)
        
        where_clause = " AND ".join(condiciones)
        
        query = f"""
            SELECT 
                DATE(AF.fecha_registro) as fecha,
                SUM(AF.ahorros) as ahorros,
                SUM(AF.actividades) as actividades,
                SUM(AF.retiros) as retiros,
                SUM(AF.saldo_final) as saldo_dia
            FROM ahorro_final AF
            WHERE {where_clause}
            GROUP BY DATE(AF.fecha_registro)
            ORDER BY fecha ASC
        """
        
        cursor.execute(query, tuple(params))
        datos = cursor.fetchall()
        
        # Calcular saldo acumulado
        saldo_acumulado = 0
        for dato in datos:
            saldo_acumulado += dato['ahorros'] + dato['actividades'] - dato['retiros']
            dato['saldo_acumulado'] = saldo_acumulado
        
        return datos
        
    except Exception as e:
        st.error(f"Error al obtener evolución de ahorros: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_distribucion_por_tipo(id_grupo, fecha_inicio=None, fecha_fin=None):
    """Obtiene la distribución de fondos por tipo"""
    # Usar las mismas funciones que el módulo de caja para consistencia
    total_multas = obtener_multas_pagadas_rango(id_grupo, fecha_inicio, fecha_fin)
    total_ahorros, total_actividades, total_retiros = obtener_ahorros_rango(id_grupo, fecha_inicio, fecha_fin)
    total_pago_prestamos, total_desembolso = obtener_prestamos_rango(id_grupo, fecha_inicio, fecha_fin)
    
    return {
        'ahorros': total_ahorros,
        'actividades': total_actividades,
        'multas_pagadas': total_multas,
        'pagos_prestamos': total_pago_prestamos,
        'retiros': total_retiros,
        'prestamos_desembolsados': total_desembolso
    }

# La función mostrar_estadisticas se mantiene igual que en la versión anterior
# Solo asegúrate de que use 'saldo_neto' para mostrar el Saldo Total

def mostrar_estadisticas(id_grupo):
    """
    Módulo de Estadísticas - Dashboard completo para miembros
    """
    
    # Verificar acceso (solo para miembros)
    rol = st.session_state.get("rol", "").lower()
    if rol != "miembro":
        st.error("❌ Este módulo está disponible solo para miembros.")
        return

    if not id_grupo:
        st.error("❌ No tiene un grupo asignado. Contacte al administrador.")
        return

    # Título principal
    st.markdown("""
    <div style='text-align: center;'>
        <h1>📊 Dashboard de Estadísticas</h1>
        <h3 style='color: #4C3A60; margin-top: -10px;'>Resumen completo del grupo</h3>
    </div>
    """, unsafe_allow_html=True)

    # ===============================
    # 1. FILTROS PRINCIPALES
    # ===============================
    st.subheader("🎛️ Filtros de Análisis")
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        fecha_inicio = st.date_input(
            "📅 Fecha inicio", 
            date.today() - timedelta(days=30),
            key="fecha_inicio_estadisticas"
        )
    
    with col2:
        fecha_fin = st.date_input(
            "📅 Fecha fin", 
            date.today(),
            key="fecha_fin_estadisticas"
        )
    
    with col3:
        # Obtener miembros para el filtro
        conn = obtener_conexion()
        miembros = []
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT M.id_miembro, M.Nombre 
                    FROM Miembros M 
                    JOIN Grupomiembros GM ON M.id_miembro = GM.id_miembro 
                    WHERE GM.id_grupo = %s
                """, (id_grupo,))
                miembros = cursor.fetchall()
                cursor.close()
            except:
                pass
            finally:
                if conn.is_connected():
                    conn.close()
        
        opciones_miembros = {m['id_miembro']: m['Nombre'] for m in miembros}
        miembro_filtro = st.selectbox(
            "👤 Filtrar por miembro:",
            options=["Todos"] + list(opciones_miembros.keys()),
            format_func=lambda x: "Todos" if x == "Todos" else opciones_miembros[x],
            key="miembro_filtro"
        )

    # ===============================
    # 2. KPI PRINCIPALES - CORREGIDOS
    # ===============================
    st.subheader("📈 Métricas Principales")
    
    # Obtener estadísticas
    id_miembro_filtro = None if miembro_filtro == "Todos" else miembro_filtro
    stats = obtener_estadisticas_grupo(id_grupo, fecha_inicio, fecha_fin, id_miembro_filtro)
    
    if stats:
        # PRIMERA FILA - 4 columnas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Saldo Total", 
                f"${stats.get('saldo_neto', 0):,.2f}",
                help="Saldo neto del período (Total Entradas - Total Salidas) - Mismo cálculo que módulo Caja"
            )
        
        with col2:
            st.metric(
                "🏦 Ahorros Acumulados", 
                f"${stats.get('total_ahorros', 0):,.2f}",
                help="Total de ahorros realizados por los miembros en el período"
            )
        
        with col3:
            st.metric(
                "⚡ Actividades", 
                f"${stats.get('total_actividades', 0):,.2f}",
                help="Ingresos por actividades grupales en el período"
            )
        
        with col4:
            st.metric(
                "👥 Miembros Activos", 
                f"{stats.get('total_miembros', 0)}",
                help="Número total de miembros en el grupo"
            )

        # SEGUNDA FILA - 4 columnas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Total Entradas
            total_entradas = stats.get('total_entrada', 0)
            st.metric(
                "📈 Total Entradas", 
                f"${total_entradas:,.2f}",
                help="Suma de todos los ingresos en el período"
            )
        
        with col2:
            # Total Salidas
            total_salidas = stats.get('total_salida', 0)
            st.metric(
                "📉 Total Salidas", 
                f"${total_salidas:,.2f}",
                help="Suma de todos los egresos en el período"
            )
        
        with col3:
            porcentaje_multas = stats.get('porcentaje_multas_pagadas', 0)
            total_multas = stats.get('multas_pagadas', 0) + stats.get('multas_pendientes', 0)
            st.metric(
                "🎯 Multas Pagadas", 
                f"{porcentaje_multas:.1f}%",
                help=f"{stats.get('multas_pagadas', 0)} de {total_multas} multas"
            )
        
        with col4:
            porcentaje_prestamos = stats.get('porcentaje_prestamos_pagados', 0)
            num_prestamos_pagados = stats.get('num_prestamos_pagados', 0)
            num_prestamos_activos = stats.get('num_prestamos_activos', 0)
            total_prestamos = num_prestamos_pagados + num_prestamos_activos
            
            texto_ayuda = f"{num_prestamos_pagados} de {total_prestamos} préstamos"
            if total_prestamos == 0:
                texto_ayuda = "No hay préstamos registrados"
            
            st.metric(
                "✅ Préstamos Pagados", 
                f"{porcentaje_prestamos:.1f}%",
                help=texto_ayuda
            )

    else:
        st.warning("No se pudieron cargar las estadísticas del grupo.")

    # ===============================
    # 3. GRÁFICOS Y VISUALIZACIONES
    # ===============================
    st.subheader("📊 Visualizaciones")
    
    tab1, tab2, tab3 = st.tabs(["📈 Evolución de Ahorros", "🥧 Distribución", "👥 Ranking Miembros"])
    
    with tab1:
        # Gráfico de evolución de ahorros
        datos_evolucion = obtener_evolucion_ahorros(id_grupo, fecha_inicio, fecha_fin, id_miembro_filtro)
        
        if datos_evolucion:
            df_evolucion = pd.DataFrame(datos_evolucion)
            df_evolucion['fecha'] = pd.to_datetime(df_evolucion['fecha'])
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_evolucion['fecha'], 
                y=df_evolucion['saldo_acumulado'],
                mode='lines+markers',
                name='Saldo Acumulado',
                line=dict(color='#4CAF50', width=3),
                marker=dict(size=6)
            ))
            
            fig.add_trace(go.Bar(
                x=df_evolucion['fecha'], 
                y=df_evolucion['ahorros'],
                name='Ahorros Diarios',
                marker_color='#2196F3',
                opacity=0.6
            ))
            
            fig.update_layout(
                title='Evolución del Saldo de Ahorros',
                xaxis_title='Fecha',
                yaxis_title='Monto ($)',
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📈 No hay datos de evolución para mostrar en el período seleccionado.")
    
    with tab2:
        # Gráfico de distribución
        distribucion = obtener_distribucion_por_tipo(id_grupo, fecha_inicio, fecha_fin)
        
        if distribucion and any(distribucion.values()):
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de ENTRADAS
                labels_entradas = ['Ahorros', 'Actividades', 'Multas Pagadas', 'Pagos Préstamos']
                values_entradas = [
                    distribucion.get('ahorros', 0),
                    distribucion.get('actividades', 0),
                    distribucion.get('multas_pagadas', 0),
                    distribucion.get('pagos_prestamos', 0)
                ]
                
                filtered_entradas = [(label, value) for label, value in zip(labels_entradas, values_entradas) if value > 0]
                if filtered_entradas:
                    labels_filtered, values_filtered = zip(*filtered_entradas)
                    
                    fig_pie_entradas = px.pie(
                        names=labels_filtered, 
                        values=values_filtered,
                        title='Distribución de Entradas',
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    
                    fig_pie_entradas.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie_entradas, use_container_width=True)
                else:
                    st.info("💵 No hay datos de entradas para mostrar.")
            
            with col2:
                # Gráfico de SALIDAS
                labels_salidas = ['Retiros', 'Préstamos Desembolsados']
                values_salidas = [
                    distribucion.get('retiros', 0),
                    distribucion.get('prestamos_desembolsados', 0)
                ]
                
                filtered_salidas = [(label, value) for label, value in zip(labels_salidas, values_salidas) if value > 0]
                if filtered_salidas:
                    labels_filtered, values_filtered = zip(*filtered_salidas)
                    
                    fig_pie_salidas = px.pie(
                        names=labels_filtered, 
                        values=values_filtered,
                        title='Distribución de Salidas',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    
                    fig_pie_salidas.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie_salidas, use_container_width=True)
                else:
                    st.info("💸 No hay datos de salidas para mostrar.")
        else:
            st.info("🥧 No hay datos de distribución para mostrar en el período seleccionado.")
    
    with tab3:
        # Ranking de miembros
        stats_miembros = obtener_estadisticas_por_miembro(id_grupo, fecha_inicio, fecha_fin)
        
        if stats_miembros:
            df_miembros = pd.DataFrame(stats_miembros)
            
            # Asegurar que la columna 'saldo_ahorro' sea numérica
            df_miembros['saldo_ahorro'] = pd.to_numeric(df_miembros['saldo_ahorro'], errors='coerce').fillna(0)
            
            # Ordenar por saldo de ahorro
            df_miembros = df_miembros.sort_values('saldo_ahorro', ascending=False)
            
            if not df_miembros.empty:
                # Tomar los top 10 o todos si hay menos de 10
                top_miembros = df_miembros.head(min(10, len(df_miembros)))
                
                fig_barras = px.bar(
                    top_miembros,
                    x='Nombre',
                    y='saldo_ahorro',
                    title='Top Miembros por Saldo Neto',
                    color='saldo_ahorro',
                    color_continuous_scale='Viridis'
                )
                
                fig_barras.update_layout(
                    xaxis_title='Miembro',
                    yaxis_title='Saldo Neto ($)',
                    height=400
                )
                
                st.plotly_chart(fig_barras, use_container_width=True)
            else:
                st.info("💰 No hay datos de miembros para mostrar en el ranking.")
            
            # Mostrar tabla completa
            with st.expander("📋 Ver tabla completa de miembros"):
                columnas_mostrar = ['Nombre', 'total_entradas', 'total_salidas', 'saldo_ahorro']
                nombres_columnas = ['Miembro', 'Total Entradas', 'Total Salidas', 'Saldo Neto']
                
                df_display = df_miembros[columnas_mostrar].copy()
                df_display.columns = nombres_columnas
                
                # Formatear números
                for col in nombres_columnas[1:]:
                    df_display[col] = df_display[col].apply(lambda x: f"${float(x):,.2f}" if pd.notna(x) else "$0.00")
                
                st.dataframe(df_display, use_container_width=True)
        else:
            st.info("👥 No hay datos de miembros para mostrar.")

    # ===============================
    # 4. REPORTE DETALLADO
    # ===============================
    st.subheader("📋 Reporte Detallado")
    
    if stats:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🟩 Entradas de Dinero")
            st.write(f"**Ahorros:** ${stats.get('total_ahorros', 0):,.2f}")
            st.write(f"**Actividades:** ${stats.get('total_actividades', 0):,.2f}")
            st.write(f"**Multas Pagadas:** ${stats.get('total_multas', 0):,.2f}")
            st.write(f"**Pagos de Préstamos:** ${stats.get('total_pago_prestamos', 0):,.2f}")
            st.write(f"**Total Entradas:** ${stats.get('total_entrada', 0):,.2f}")
        
        with col2:
            st.markdown("#### 🟥 Salidas de Dinero")
            st.write(f"**Retiros:** ${stats.get('total_retiros', 0):,.2f}")
            st.write(f"**Préstamos Desembolsados:** ${stats.get('total_desembolso', 0):,.2f}")
            st.write(f"**Total Salidas:** ${stats.get('total_salida', 0):,.2f}")
        
        st.markdown("---")
        st.markdown(f"#### 📊 Resumen General")
        st.write(f"**Período analizado:** {fecha_inicio} al {fecha_fin}")
        if id_miembro_filtro:
            st.write(f"**Miembro filtrado:** {opciones_miembros.get(id_miembro_filtro, 'N/A')}")
        
        # Fórmula detallada del saldo neto
        st.write(f"**Fórmula del Saldo Neto:**")
        st.write(f"Entradas (${stats.get('total_entrada', 0):,.2f}) - " +
                f"Salidas (${stats.get('total_salida', 0):,.2f}) = " +
                f"**${stats.get('saldo_neto', 0):,.2f}**")

    # ===============================
    # 5. BOTÓN REGRESAR
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    # Información del período
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **📅 Período Actual:**
    - Inicio: {fecha_inicio}
    - Fin: {fecha_fin}
    - Miembro: {'Todos' if not id_miembro_filtro else opciones_miembros.get(id_miembro_filtro, 'N/A')}
    
    **📝 Fórmula Saldo:**
    Total Entradas - Total Salidas
    - Mismo cálculo que módulo Caja
    """)
