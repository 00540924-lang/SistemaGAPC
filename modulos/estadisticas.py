import streamlit as st
import mysql.connector
from datetime import date, datetime, timedelta
from modulos.config.conexion import obtener_conexion
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def obtener_estadisticas_grupo(id_grupo, fecha_inicio=None, fecha_fin=None, id_miembro=None):
    """Obtiene estadísticas completas del grupo o de un miembro específico"""
    conn = obtener_conexion()
    if not conn:
        return {}
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # Construir condiciones WHERE dinámicas - CORREGIDO: sin PP.fecha
        condiciones = ["GM.id_grupo = %s"]
        params = [id_grupo]
        
        if fecha_inicio and fecha_fin:
            # Solo usar fechas de tablas existentes
            condiciones.append("(AF.fecha_registro BETWEEN %s AND %s OR MT.fecha BETWEEN %s AND %s OR P.fecha_desembolso BETWEEN %s AND %s)")
            params.extend([fecha_inicio, fecha_fin] * 3)
        
        if id_miembro:
            condiciones.append("M.id_miembro = %s")
            params.append(id_miembro)
        
        where_clause = " AND ".join(condiciones)
        
        # Consulta principal para estadísticas - CORREGIDA
        query = f"""
            SELECT 
                -- Estadísticas de ahorros
                COALESCE(SUM(AF.ahorros), 0) as total_ahorros,
                COALESCE(SUM(AF.actividades), 0) as total_actividades,
                COALESCE(SUM(AF.retiros), 0) as total_retiros,
                COALESCE(SUM(AF.saldo_final), 0) as saldo_total_ahorros,
                
                -- Estadísticas de multas
                COALESCE(SUM(MT.monto_a_pagar), 0) as total_multas,
                COUNT(DISTINCT CASE WHEN MT.pagada = 1 THEN MT.id_multa END) as multas_pagadas,
                COUNT(DISTINCT CASE WHEN MT.pagada = 0 THEN MT.id_multa END) as multas_pendientes,
                
                -- Estadísticas de préstamos (CORREGIDO)
                COALESCE(SUM(CASE WHEN P.estado = 'activo' THEN P.monto ELSE 0 END), 0) as prestamos_activos,
                COALESCE(SUM(CASE WHEN P.estado = 'pagado' THEN P.monto ELSE 0 END), 0) as prestamos_pagados,
                COUNT(DISTINCT CASE WHEN P.estado = 'activo' THEN P.id_prestamo END) as num_prestamos_activos,
                COUNT(DISTINCT CASE WHEN P.estado = 'pagado' THEN P.id_prestamo END) as num_prestamos_pagados,
                
                -- Estadísticas generales
                COUNT(DISTINCT M.id_miembro) as total_miembros,
                COUNT(DISTINCT AF.id_ahorro) as total_registros_ahorro
                
            FROM Miembros M
            JOIN Grupomiembros GM ON M.id_miembro = GM.id_miembro
            LEFT JOIN ahorro_final AF ON M.id_miembro = AF.id_miembro AND AF.id_grupo = GM.id_grupo
            LEFT JOIN Multas MT ON M.id_miembro = MT.id_miembro
            LEFT JOIN prestamos P ON M.id_miembro = P.id_miembro
            WHERE {where_clause}
        """
        
        cursor.execute(query, tuple(params))
        estadisticas = cursor.fetchone()
        
        # Calcular métricas adicionales
        if estadisticas:
            # CORRECCIÓN: Calcular saldo neto correctamente (misma lógica que módulo de préstamos)
            estadisticas['saldo_neto'] = (
                estadisticas['total_ahorros'] + 
                estadisticas['total_actividades'] + 
                estadisticas['total_multas'] - 
                estadisticas['total_retiros'] - 
                estadisticas['prestamos_activos']
            )
            
            # Calcular total egresos
            estadisticas['total_egresos'] = (
                estadisticas['total_retiros'] + 
                estadisticas['prestamos_activos']
            )
            
            # Porcentajes
            total_multas = estadisticas['multas_pagadas'] + estadisticas['multas_pendientes']
            if total_multas > 0:
                estadisticas['porcentaje_multas_pagadas'] = (
                    estadisticas['multas_pagadas'] / total_multas * 100
                )
            else:
                estadisticas['porcentaje_multas_pagadas'] = 0
                
            # CORRECCIÓN MEJORADA: Lógica para préstamos pagados
            total_prestamos = estadisticas['num_prestamos_activos'] + estadisticas['num_prestamos_pagados']
            if total_prestamos > 0:
                estadisticas['porcentaje_prestamos_pagados'] = (
                    estadisticas['num_prestamos_pagados'] / total_prestamos * 100
                )
            else:
                estadisticas['porcentaje_prestamos_pagados'] = 0
            
            # Si no hay préstamos activos pero sí hay préstamos pagados, forzar 100%
            if estadisticas['num_prestamos_pagados'] > 0 and estadisticas['num_prestamos_activos'] == 0:
                estadisticas['porcentaje_prestamos_pagados'] = 100.0
        
        return estadisticas or {}
        
    except Exception as e:
        st.error(f"Error al obtener estadísticas: {e}")
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
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # Construir condiciones WHERE dinámicas - CORREGIDO
        condiciones = ["GM.id_grupo = %s"]
        params = [id_grupo]
        
        if fecha_inicio and fecha_fin:
            condiciones.append("(AF.fecha_registro BETWEEN %s AND %s OR MT.fecha BETWEEN %s AND %s OR P.fecha_desembolso BETWEEN %s AND %s)")
            params.extend([fecha_inicio, fecha_fin] * 3)
        
        where_clause = " AND ".join(condiciones)
        
        query = f"""
            SELECT 
                M.id_miembro,
                M.Nombre,
                
                -- Ahorros del miembro
                COALESCE(SUM(AF.ahorros), 0) as total_ahorros,
                COALESCE(SUM(AF.actividades), 0) as total_actividades,
                COALESCE(SUM(AF.retiros), 0) as total_retiros,
                
                -- Multas del miembro
                COALESCE(SUM(MT.monto_a_pagar), 0) as total_multas,
                COUNT(DISTINCT CASE WHEN MT.pagada = 1 THEN MT.id_multa END) as multas_pagadas,
                COUNT(DISTINCT CASE WHEN MT.pagada = 0 THEN MT.id_multa END) as multas_pendientes,
                
                -- Préstamos del miembro (AGREGADO)
                COALESCE(SUM(CASE WHEN P.estado = 'activo' THEN P.monto ELSE 0 END), 0) as prestamos_activos
                
            FROM Miembros M
            JOIN Grupomiembros GM ON M.id_miembro = GM.id_miembro
            LEFT JOIN ahorro_final AF ON M.id_miembro = AF.id_miembro AND AF.id_grupo = GM.id_grupo
            LEFT JOIN Multas MT ON M.id_miembro = MT.id_miembro
            LEFT JOIN prestamos P ON M.id_miembro = P.id_miembro
            WHERE {where_clause}
            GROUP BY M.id_miembro, M.Nombre
            ORDER BY total_ahorros DESC
        """
        
        cursor.execute(query, tuple(params))
        resultados = cursor.fetchall()
        
        # Calcular saldo correcto para cada miembro (misma lógica que módulo de préstamos)
        for miembro in resultados:
            miembro['saldo_ahorro'] = (
                miembro['total_ahorros'] + 
                miembro['total_actividades'] + 
                miembro['total_multas'] - 
                miembro['total_retiros'] - 
                miembro['prestamos_activos']
            )
        
        return resultados
        
    except Exception as e:
        st.error(f"Error al obtener estadísticas por miembro: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

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
    conn = obtener_conexion()
    if not conn:
        return {}
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        condiciones = ["GM.id_grupo = %s"]
        params = [id_grupo]
        
        if fecha_inicio and fecha_fin:
            condiciones.append("(AF.fecha_registro BETWEEN %s AND %s OR MT.fecha BETWEEN %s AND %s OR P.fecha_desembolso BETWEEN %s AND %s)")
            params.extend([fecha_inicio, fecha_fin] * 3)
        
        where_clause = " AND ".join(condiciones)
        
        query = f"""
            SELECT 
                -- Ahorros
                COALESCE(SUM(AF.ahorros), 0) as ahorros,
                COALESCE(SUM(AF.actividades), 0) as actividades,
                COALESCE(SUM(AF.retiros), 0) as retiros,
                
                -- Multas
                COALESCE(SUM(MT.monto_a_pagar), 0) as multas,
                
                -- Préstamos activos
                COALESCE(SUM(CASE WHEN P.estado = 'activo' THEN P.monto ELSE 0 END), 0) as prestamos_activos
                
            FROM Grupomiembros GM
            LEFT JOIN ahorro_final AF ON GM.id_miembro = AF.id_miembro AND AF.id_grupo = GM.id_grupo
            LEFT JOIN Multas MT ON GM.id_miembro = MT.id_miembro
            LEFT JOIN prestamos P ON GM.id_miembro = P.id_miembro
            WHERE {where_clause}
        """
        
        cursor.execute(query, tuple(params))
        return cursor.fetchone() or {}
        
    except Exception as e:
        st.error(f"Error al obtener distribución por tipo: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

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
                help="Saldo neto del grupo (ahorros + actividades + multas - retiros - préstamos activos)"
            )
        
        with col2:
            st.metric(
                "🏦 Ahorros Acumulados", 
                f"${stats.get('total_ahorros', 0):,.2f}",
                help="Total de ahorros realizados por los miembros"
            )
        
        with col3:
            st.metric(
                "⚡ Actividades", 
                f"${stats.get('total_actividades', 0):,.2f}",
                help="Ingresos por actividades grupales"
            )
        
        with col4:
            # CORRECCIÓN: Obtener el número real de miembros del grupo
            conn = obtener_conexion()
            total_miembros_real = 0
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM Grupomiembros 
                        WHERE id_grupo = %s
                    """, (id_grupo,))
                    total_miembros_real = cursor.fetchone()[0]
                    cursor.close()
                except:
                    total_miembros_real = stats.get('total_miembros', 0)
                finally:
                    if conn.is_connected():
                        conn.close()
            else:
                total_miembros_real = stats.get('total_miembros', 0)
            
            st.metric(
                "👥 Miembros Activos", 
                f"{total_miembros_real}",
                help="Número total de miembros en el grupo"
            )

        # SEGUNDA FILA - 4 columnas (CORREGIDA - SIN REGISTROS DE AHORRO)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # NUEVA MÉTRICA: Total Egresos
            total_egresos = stats.get('total_egresos', 0)
            st.metric(
                "📉 Total Egresos", 
                f"${total_egresos:,.2f}",
                help="Total de retiros y préstamos activos"
            )
        
        with col2:
            porcentaje_multas = stats.get('porcentaje_multas_pagadas', 0)
            total_multas = stats.get('multas_pagadas', 0) + stats.get('multas_pendientes', 0)
            st.metric(
                "🎯 Multas Pagadas", 
                f"{porcentaje_multas:.1f}%",
                help=f"{stats.get('multas_pagadas', 0)} de {total_multas} multas"
            )
        
        with col3:
            # CORRECCIÓN: Lógica mejorada para préstamos pagados
            porcentaje_prestamos = stats.get('porcentaje_prestamos_pagados', 0)
            num_prestamos_pagados = stats.get('num_prestamos_pagados', 0)
            num_prestamos_activos = stats.get('num_prestamos_activos', 0)
            total_prestamos = num_prestamos_pagados + num_prestamos_activos
            
            # Texto de ayuda
            texto_ayuda = f"{num_prestamos_pagados} de {total_prestamos} préstamos"
            if total_prestamos == 0:
                texto_ayuda = "No hay préstamos registrados"
            
            st.metric(
                "✅ Préstamos Pagados", 
                f"{porcentaje_prestamos:.1f}%",
                help=texto_ayuda
            )
        
        with col4:
            # Mostrar total de multas como métrica adicional
            total_multas_monto = stats.get('total_multas', 0)
            st.metric(
                "⚖️ Total Multas", 
                f"${total_multas_monto:,.2f}",
                help="Total de multas registradas en el período"
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
            # Crear dos gráficos: uno para ingresos y otro para egresos
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de ingresos
                labels_ingresos = ['Ahorros', 'Actividades', 'Multas']
                values_ingresos = [
                    distribucion.get('ahorros', 0),
                    distribucion.get('actividades', 0),
                    distribucion.get('multas', 0)
                ]
                
                # Filtrar categorías con valores > 0
                filtered_ingresos = [(label, value) for label, value in zip(labels_ingresos, values_ingresos) if value > 0]
                if filtered_ingresos:
                    labels_filtered, values_filtered = zip(*filtered_ingresos)
                    
                    fig_pie_ingresos = px.pie(
                        names=labels_filtered, 
                        values=values_filtered,
                        title='Distribución de Ingresos',
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    
                    fig_pie_ingresos.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie_ingresos, use_container_width=True)
                else:
                    st.info("💵 No hay datos de ingresos para mostrar.")
            
            with col2:
                # Gráfico de egresos
                labels_egresos = ['Retiros', 'Préstamos Activos']
                values_egresos = [
                    distribucion.get('retiros', 0),
                    distribucion.get('prestamos_activos', 0)
                ]
                
                # Filtrar categorías con valores > 0
                filtered_egresos = [(label, value) for label, value in zip(labels_egresos, values_egresos) if value > 0]
                if filtered_egresos:
                    labels_filtered, values_filtered = zip(*filtered_egresos)
                    
                    fig_pie_egresos = px.pie(
                        names=labels_filtered, 
                        values=values_filtered,
                        title='Distribución de Egresos',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    
                    fig_pie_egresos.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie_egresos, use_container_width=True)
                else:
                    st.info("💸 No hay datos de egresos para mostrar.")
        else:
            st.info("🥧 No hay datos de distribución para mostrar en el período seleccionado.")
    
    with tab3:
        # Ranking de miembros
        stats_miembros = obtener_estadisticas_por_miembro(id_grupo, fecha_inicio, fecha_fin)
        
        if stats_miembros:
            df_miembros = pd.DataFrame(stats_miembros)
            
            # Asegurar que la columna 'saldo_ahorro' sea numérica
            df_miembros['saldo_ahorro'] = pd.to_numeric(df_miembros['saldo_ahorro'], errors='coerce').fillna(0)
            
            # Ordenar por saldo de ahorro (puede ser positivo o negativo)
            df_miembros = df_miembros.sort_values('saldo_ahorro', ascending=False)
            
            if not df_miembros.empty:
                # Tomar los top 10 o todos si hay menos de 10
                top_miembros = df_miembros.head(min(10, len(df_miembros)))
                
                fig_barras = px.bar(
                    top_miembros,
                    x='Nombre',
                    y='saldo_ahorro',
                    title='Top Miembros por Saldo de Ahorro',
                    color='saldo_ahorro',
                    color_continuous_scale='Viridis'
                )
                
                fig_barras.update_layout(
                    xaxis_title='Miembro',
                    yaxis_title='Saldo de Ahorro ($)',
                    height=400
                )
                
                st.plotly_chart(fig_barras, use_container_width=True)
            else:
                st.info("💰 No hay datos de miembros para mostrar en el ranking.")
            
            # Mostrar tabla completa
            with st.expander("📋 Ver tabla completa de miembros"):
                columnas_mostrar = ['Nombre', 'total_ahorros', 'total_actividades', 'total_retiros', 'total_multas', 'prestamos_activos', 'saldo_ahorro']
                nombres_columnas = ['Miembro', 'Ahorros', 'Actividades', 'Retiros', 'Multas', 'Préstamos Activos', 'Saldo Neto']
                
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
            st.write(f"**Multas:** ${stats.get('total_multas', 0):,.2f}")
            total_entradas = stats.get('total_ahorros', 0) + stats.get('total_actividades', 0) + stats.get('total_multas', 0)
            st.write(f"**Total Entradas:** ${total_entradas:,.2f}")
        
        with col2:
            st.markdown("#### 🟥 Salidas de Dinero")
            st.write(f"**Retiros:** ${stats.get('total_retiros', 0):,.2f}")
            st.write(f"**Préstamos Activos:** ${stats.get('prestamos_activos', 0):,.2f}")
            st.write(f"**Total Egresos:** ${stats.get('total_egresos', 0):,.2f}")
        
        st.markdown("---")
        st.markdown(f"#### 📊 Resumen General")
        st.write(f"**Período analizado:** {fecha_inicio} al {fecha_fin}")
        if id_miembro_filtro:
            st.write(f"**Miembro filtrado:** {opciones_miembros.get(id_miembro_filtro, 'N/A')}")
        
        # Fórmula detallada del saldo neto
        st.write(f"**Fórmula del Saldo Neto:**")
        st.write(f"Ahorros (${stats.get('total_ahorros', 0):,.2f}) + " +
                f"Actividades (${stats.get('total_actividades', 0):,.2f}) + " +
                f"Multas (${stats.get('total_multas', 0):,.2f}) - " +
                f"Retiros (${stats.get('total_retiros', 0):,.2f}) - " +
                f"Préstamos Activos (${stats.get('prestamos_activos', 0):,.2f}) = " +
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
    Ahorros + Actividades + Multas - Retiros - Préstamos Activos
    """)
