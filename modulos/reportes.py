import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def obtener_estadisticas_por_grupo(id_grupo, fecha_inicio, fecha_fin):
    """
    Obtiene estadísticas de ingresos, egresos y saldo para un grupo específico
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return None
            
        cursor = conn.cursor(dictionary=True)
        
        # Obtener INGRESOS (Dinero que ENTRA)
        # 1. Multas pagadas
        cursor.execute("""
            SELECT COALESCE(SUM(MT.monto_a_pagar), 0) as total_multas
            FROM Multas MT
            JOIN Miembros M ON MT.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            AND MT.fecha BETWEEN %s AND %s
            AND MT.pagada = 1
        """, (id_grupo, fecha_inicio, fecha_fin))
        multas = cursor.fetchone()['total_multas']
        
        # 2. Ahorros y actividades
        cursor.execute("""
            SELECT 
                COALESCE(SUM(ahorros), 0) as total_ahorros,
                COALESCE(SUM(actividades), 0) as total_actividades
            FROM ahorro_final 
            WHERE id_grupo = %s AND fecha_registro BETWEEN %s AND %s
        """, (id_grupo, fecha_inicio, fecha_fin))
        ahorros_result = cursor.fetchone()
        ahorros = ahorros_result['total_ahorros']
        actividades = ahorros_result['total_actividades']
        
        # 3. Pagos de préstamos (capital + interés)
        cursor.execute("""
            SELECT COALESCE(SUM(PP.capital + PP.interes), 0) as total_pagos_prestamos
            FROM prestamo_pagos PP
            JOIN prestamos P ON PP.id_prestamo = P.id_prestamo
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s 
            AND PP.fecha BETWEEN %s AND %s
            AND PP.estado = 'pagado'
        """, (id_grupo, fecha_inicio, fecha_fin))
        pagos_prestamos = cursor.fetchone()['total_pagos_prestamos']
        
        # Calcular total ingresos
        total_ingresos = multas + ahorros + actividades + pagos_prestamos
        
        # Obtener EGRESOS (Dinero que SALE)
        # 1. Retiros de ahorros
        cursor.execute("""
            SELECT COALESCE(SUM(retiros), 0) as total_retiros
            FROM ahorro_final 
            WHERE id_grupo = %s AND fecha_registro BETWEEN %s AND %s
        """, (id_grupo, fecha_inicio, fecha_fin))
        retiros = cursor.fetchone()['total_retiros']
        
        # 2. Desembolsos de préstamos
        cursor.execute("""
            SELECT COALESCE(SUM(P.monto), 0) as total_desembolsos
            FROM prestamos P
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s 
            AND P.fecha_desembolso BETWEEN %s AND %s
            AND P.estado IN ('activo', 'pendiente')
        """, (id_grupo, fecha_inicio, fecha_fin))
        desembolsos = cursor.fetchone()['total_desembolsos']
        
        # Calcular total egresos
        total_egresos = retiros + desembolsos
        
        # Calcular saldo neto
        saldo_neto = total_ingresos - total_egresos
        
        conn.close()
        
        return {
            'grupo_id': id_grupo,
            'ingresos': {
                'multas': float(multas),
                'ahorros': float(ahorros),
                'actividades': float(actividades),
                'pagos_prestamos': float(pagos_prestamos),
                'total': float(total_ingresos)
            },
            'egresos': {
                'retiros': float(retiros),
                'desembolsos': float(desembolsos),
                'total': float(total_egresos)
            },
            'saldo_neto': float(saldo_neto)
        }
        
    except Exception as e:
        st.error(f"Error al obtener estadísticas del grupo: {e}")
        return None

def obtener_estadisticas_por_distrito(fecha_inicio, fecha_fin):
    """
    Obtiene estadísticas de ingresos, egresos y saldo agrupadas por distrito
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return None
            
        cursor = conn.cursor(dictionary=True)
        
        # Obtener estadísticas por distrito
        cursor.execute("""
            SELECT 
                G.distrito,
                COALESCE(SUM(
                    (SELECT COALESCE(SUM(MT.monto_a_pagar), 0)
                     FROM Multas MT
                     JOIN Miembros M2 ON MT.id_miembro = M2.id_miembro
                     JOIN Grupomiembros GM2 ON GM2.id_miembro = M2.id_miembro
                     WHERE GM2.id_grupo = G.id_grupo
                     AND MT.fecha BETWEEN %s AND %s
                     AND MT.pagada = 1)
                ), 0) as total_multas,
                
                COALESCE(SUM(
                    (SELECT COALESCE(SUM(ahorros + actividades), 0)
                     FROM ahorro_final AF
                     WHERE AF.id_grupo = G.id_grupo
                     AND AF.fecha_registro BETWEEN %s AND %s)
                ), 0) as total_ahorros_actividades,
                
                COALESCE(SUM(
                    (SELECT COALESCE(SUM(PP.capital + PP.interes), 0)
                     FROM prestamo_pagos PP
                     JOIN prestamos P2 ON PP.id_prestamo = P2.id_prestamo
                     JOIN Miembros M3 ON P2.id_miembro = M3.id_miembro
                     JOIN Grupomiembros GM3 ON GM3.id_miembro = M3.id_miembro
                     WHERE GM3.id_grupo = G.id_grupo
                     AND PP.fecha BETWEEN %s AND %s
                     AND PP.estado = 'pagado')
                ), 0) as total_pagos_prestamos,
                
                COALESCE(SUM(
                    (SELECT COALESCE(SUM(retiros), 0)
                     FROM ahorro_final AF2
                     WHERE AF2.id_grupo = G.id_grupo
                     AND AF2.fecha_registro BETWEEN %s AND %s)
                ), 0) as total_retiros,
                
                COALESCE(SUM(
                    (SELECT COALESCE(SUM(P3.monto), 0)
                     FROM prestamos P3
                     JOIN Miembros M4 ON P3.id_miembro = M4.id_miembro
                     JOIN Grupomiembros GM4 ON GM4.id_miembro = M4.id_miembro
                     WHERE GM4.id_grupo = G.id_grupo
                     AND P3.fecha_desembolso BETWEEN %s AND %s
                     AND P3.estado IN ('activo', 'pendiente'))
                ), 0) as total_desembolsos
                
            FROM Grupos G
            GROUP BY G.distrito
            ORDER BY G.distrito
        """, (fecha_inicio, fecha_fin,
              fecha_inicio, fecha_fin,
              fecha_inicio, fecha_fin,
              fecha_inicio, fecha_fin,
              fecha_inicio, fecha_fin))
        
        resultados = cursor.fetchall()
        conn.close()
        
        # Procesar resultados
        estadisticas_distritos = []
        for resultado in resultados:
            distrito = resultado['distrito']
            total_ingresos = (resultado['total_multas'] + 
                            resultado['total_ahorros_actividades'] + 
                            resultado['total_pagos_prestamos'])
            total_egresos = resultado['total_retiros'] + resultado['total_desembolsos']
            saldo_neto = total_ingresos - total_egresos
            
            estadisticas_distritos.append({
                'distrito': distrito,
                'ingresos': {
                    'multas': float(resultado['total_multas']),
                    'ahorros_actividades': float(resultado['total_ahorros_actividades']),
                    'pagos_prestamos': float(resultado['total_pagos_prestamos']),
                    'total': float(total_ingresos)
                },
                'egresos': {
                    'retiros': float(resultado['total_retiros']),
                    'desembolsos': float(resultado['total_desembolsos']),
                    'total': float(total_egresos)
                },
                'saldo_neto': float(saldo_neto)
            })
        
        return estadisticas_distritos
        
    except Exception as e:
        st.error(f"Error al obtener estadísticas por distrito: {e}")
        return None

def obtener_ranking_grupos_por_ingresos(fecha_inicio, fecha_fin):
    """
    Obtiene el ranking de grupos ordenados por ingresos totales
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return []
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                G.id_grupo,
                G.Nombre_grupo,
                G.distrito,
                COALESCE(SUM(
                    (SELECT COALESCE(SUM(MT.monto_a_pagar), 0)
                     FROM Multas MT
                     JOIN Miembros M2 ON MT.id_miembro = M2.id_miembro
                     JOIN Grupomiembros GM2 ON GM2.id_miembro = M2.id_miembro
                     WHERE GM2.id_grupo = G.id_grupo
                     AND MT.fecha BETWEEN %s AND %s
                     AND MT.pagada = 1)
                ), 0) as total_multas,
                
                COALESCE(SUM(
                    (SELECT COALESCE(SUM(ahorros + actividades), 0)
                     FROM ahorro_final AF
                     WHERE AF.id_grupo = G.id_grupo
                     AND AF.fecha_registro BETWEEN %s AND %s)
                ), 0) as total_ahorros_actividades,
                
                COALESCE(SUM(
                    (SELECT COALESCE(SUM(PP.capital + PP.interes), 0)
                     FROM prestamo_pagos PP
                     JOIN prestamos P2 ON PP.id_prestamo = P2.id_prestamo
                     JOIN Miembros M3 ON P2.id_miembro = M3.id_miembro
                     JOIN Grupomiembros GM3 ON GM3.id_miembro = M3.id_miembro
                     WHERE GM3.id_grupo = G.id_grupo
                     AND PP.fecha BETWEEN %s AND %s
                     AND PP.estado = 'pagado')
                ), 0) as total_pagos_prestamos
                
            FROM Grupos G
            GROUP BY G.id_grupo, G.Nombre_grupo, G.distrito
            HAVING (total_multas + total_ahorros_actividades + total_pagos_prestamos) > 0
            ORDER BY (total_multas + total_ahorros_actividades + total_pagos_prestamos) DESC
        """, (fecha_inicio, fecha_fin,
              fecha_inicio, fecha_fin,
              fecha_inicio, fecha_fin))
        
        resultados = cursor.fetchall()
        conn.close()
        
        # Procesar resultados
        ranking_grupos = []
        for resultado in resultados:
            total_ingresos = (resultado['total_multas'] + 
                            resultado['total_ahorros_actividades'] + 
                            resultado['total_pagos_prestamos'])
            
            ranking_grupos.append({
                'grupo_id': resultado['id_grupo'],
                'nombre_grupo': resultado['Nombre_grupo'],
                'distrito': resultado['distrito'],
                'ingresos_total': float(total_ingresos),
                'multas': float(resultado['total_multas']),
                'ahorros_actividades': float(resultado['total_ahorros_actividades']),
                'pagos_prestamos': float(resultado['total_pagos_prestamos'])
            })
        
        return ranking_grupos
        
    except Exception as e:
        st.error(f"Error al obtener ranking de grupos: {e}")
        return []

def obtener_nombre_grupo(id_grupo):
    """Obtiene el nombre del grupo por su ID"""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT Nombre_grupo FROM Grupos WHERE id_grupo = %s", (id_grupo,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else f"Grupo {id_grupo}"
    except:
        return f"Grupo {id_grupo}"

def obtener_todos_los_grupos():
    """Obtiene todos los grupos disponibles (para usuarios institucionales)"""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id_grupo, Nombre_grupo FROM Grupos ORDER BY Nombre_grupo")
        grupos = cursor.fetchall()
        conn.close()
        return grupos
    except Exception as e:
        st.error(f"Error al obtener grupos: {e}")
        return []

def mostrar_kpis_promotor(estadisticas, nombre_grupo):
    """Muestra KPIs para promotor con diseño mejorado"""
    st.markdown(f"### 📊 Métricas del Grupo: {nombre_grupo}")
    
    # KPIs en 3 columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💰 Total Ingresos", 
            f"${estadisticas['ingresos']['total']:,.2f}",
            help="Suma de todos los ingresos del grupo"
        )
    
    with col2:
        st.metric(
            "💸 Total Egresos", 
            f"${estadisticas['egresos']['total']:,.2f}",
            help="Suma de todos los egresos del grupo",
            delta=f"-${estadisticas['egresos']['total']:,.2f}",
            delta_color="inverse"
        )
    
    with col3:
        color_saldo = "normal" if estadisticas['saldo_neto'] >= 0 else "inverse"
        st.metric(
            "🏦 Saldo Neto", 
            f"${estadisticas['saldo_neto']:,.2f}",
            help="Saldo neto (Ingresos - Egresos)",
            delta=f"{estadisticas['saldo_neto']:,.2f}",
            delta_color=color_saldo
        )

def mostrar_kpis_institucional(estadisticas_distritos, distrito_seleccionado="Todos"):
    """Muestra KPIs para institucional con diseño mejorado"""
    st.markdown("### 📊 Métricas por Distrito")
    
    # Filtrar datos si se seleccionó un distrito específico
    if distrito_seleccionado != "Todos":
        estadisticas_filtradas = [stats for stats in estadisticas_distritos if stats['distrito'] == distrito_seleccionado]
        if not estadisticas_filtradas:
            st.warning(f"No se encontraron datos para el distrito: {distrito_seleccionado}")
            return
        # Usar el primer (y único) elemento del distrito seleccionado
        stats = estadisticas_filtradas[0]
        total_ingresos = stats['ingresos']['total']
        total_egresos = stats['egresos']['total']
        total_saldo = stats['saldo_neto']
        titulo_sufijo = f" - {distrito_seleccionado}"
    else:
        # Calcular totales generales para todos los distritos
        total_ingresos = sum(stats['ingresos']['total'] for stats in estadisticas_distritos)
        total_egresos = sum(stats['egresos']['total'] for stats in estadisticas_distritos)
        total_saldo = total_ingresos - total_egresos
        titulo_sufijo = ""
    
    # KPIs en 3 columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            f"💰 Ingresos Totales{titulo_sufijo}", 
            f"${total_ingresos:,.2f}",
            help="Suma de ingresos" + (" del distrito" if distrito_seleccionado != "Todos" else " de todos los distritos")
        )
    
    with col2:
        st.metric(
            f"💸 Egresos Totales{titulo_sufijo}", 
            f"${total_egresos:,.2f}",
            help="Suma de egresos" + (" del distrito" if distrito_seleccionado != "Todos" else " de todos los distritos"),
            delta=f"-${total_egresos:,.2f}",
            delta_color="inverse"
        )
    
    with col3:
        color_saldo = "normal" if total_saldo >= 0 else "inverse"
        st.metric(
            f"🏦 Saldo Neto Total{titulo_sufijo}", 
            f"${total_saldo:,.2f}",
            help="Saldo neto (Ingresos - Egresos)" + (" del distrito" if distrito_seleccionado != "Todos" else " de todos los distritos"),
            delta=f"{total_saldo:,.2f}",
            delta_color=color_saldo
        )

def crear_grafico_tendencias_distritos(estadisticas_distritos):
    """Crea gráfico de tendencias para distritos usando Plotly"""
    
    # Preparar datos
    distritos = [stats['distrito'] for stats in estadisticas_distritos]
    ingresos = [stats['ingresos']['total'] for stats in estadisticas_distritos]
    egresos = [stats['egresos']['total'] for stats in estadisticas_distritos]
    saldos = [stats['saldo_neto'] for stats in estadisticas_distritos]
    
    fig = go.Figure()
    
    # Línea de ingresos
    fig.add_trace(go.Scatter(
        x=distritos, 
        y=ingresos,
        mode='lines+markers',
        name='Ingresos',
        line=dict(color='#2E7D32', width=4),
        marker=dict(size=8, symbol='circle')
    ))
    
    # Línea de egresos
    fig.add_trace(go.Scatter(
        x=distritos, 
        y=egresos,
        mode='lines+markers',
        name='Egresos',
        line=dict(color='#C62828', width=4),
        marker=dict(size=8, symbol='square')
    ))
    
    # Línea de saldo neto
    fig.add_trace(go.Scatter(
        x=distritos, 
        y=saldos,
        mode='lines+markers',
        name='Saldo Neto',
        line=dict(color='#1565C0', width=4),
        marker=dict(size=8, symbol='triangle-up')
    ))
    
    fig.update_layout(
        title=dict(
            text='📈 Tendencias Financieras por Distrito',
            font=dict(size=20, color='#4C3A60')
        ),
        xaxis_title='Distritos',
        yaxis_title='Monto ($)',
        hovermode='x unified',
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4C3A60'),
        xaxis=dict(tickangle=45)
    )
    
    return fig

def crear_grafico_ranking_grupos(ranking_grupos):
    """Crea gráfico de barras VERTICALES para ranking de grupos por ingresos"""
    
    if not ranking_grupos:
        return None
    
    # Limitar a top 10 grupos para mejor visualización
    top_grupos = ranking_grupos[:10]
    
    # Preparar datos
    nombres_grupos = [grupo['nombre_grupo'] for grupo in top_grupos]
    ingresos_totales = [grupo['ingresos_total'] for grupo in top_grupos]
    distritos = [grupo['distrito'] for grupo in top_grupos]
    
    # Crear gráfico de barras VERTICALES
    fig = px.bar(
        x=nombres_grupos,
        y=ingresos_totales,
        title='🏆 Ranking de Grupos por Ingresos',
        labels={'x': 'Grupos', 'y': 'Ingresos Totales ($)'},
        color=ingresos_totales,
        color_continuous_scale='Viridis',
        hover_data={'Distrito': distritos}
    )
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4C3A60'),
        xaxis=dict(tickangle=45, tickmode='array'),
        coloraxis_showscale=False
    )
    
    # Agregar valores en las barras
    fig.update_traces(
        texttemplate='$%{y:,.0f}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Ingresos: $%{y:,.2f}<br>Distrito: %{customdata[0]}<extra></extra>'
    )
    
    return fig

def crear_grafico_distribucion(estadisticas, es_distrito=False):
    """Crea gráfico de distribución usando Plotly"""
    if es_distrito:
        # Para distritos, mostrar distribución entre distritos
        labels = [stats['distrito'] for stats in estadisticas]
        ingresos = [stats['ingresos']['total'] for stats in estadisticas]
        
        fig = px.pie(
            names=labels, 
            values=ingresos,
            title='🥧 Distribución de Ingresos por Distrito',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
    else:
        # Para grupo individual, mostrar distribución por concepto
        labels = ['Ahorros', 'Actividades', 'Multas', 'Pagos Préstamos']
        values = [
            estadisticas['ingresos']['ahorros'],
            estadisticas['ingresos']['actividades'],
            estadisticas['ingresos']['multas'],
            estadisticas['ingresos']['pagos_prestamos']
        ]
        
        fig = px.pie(
            names=labels, 
            values=values,
            title='🥧 Distribución de Ingresos por Concepto',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=400,
        font=dict(color='#4C3A60')
    )
    
    return fig

def mostrar_reporte_promotor(fecha_inicio, fecha_fin):
    """Muestra el reporte para un promotor con diseño mejorado"""
    
    # Obtener todos los grupos para que el promotor seleccione
    grupos = obtener_todos_los_grupos()
    
    if not grupos:
        st.warning("No se encontraron grupos en el sistema.")
        return
    
    # Crear lista de grupos para selección
    opciones_grupos = {f"{nombre}": id_grupo for id_grupo, nombre in grupos}
    
    # Selectbox para elegir grupo
    grupo_seleccionado = st.selectbox(
        "👥 Seleccione un grupo para analizar:",
        options=list(opciones_grupos.keys())
    )
    
    if grupo_seleccionado:
        id_grupo_seleccionado = opciones_grupos[grupo_seleccionado]
        
        # Obtener estadísticas del grupo seleccionado
        estadisticas = obtener_estadisticas_por_grupo(id_grupo_seleccionado, fecha_inicio, fecha_fin)
        
        # Obtener ranking de grupos por ingresos
        ranking_grupos = obtener_ranking_grupos_por_ingresos(fecha_inicio, fecha_fin)
        
        if not estadisticas and not ranking_grupos:
            st.warning("No se encontraron datos para el período seleccionado.")
            return
        
        # Mostrar KPIs si hay estadísticas del grupo seleccionado
        if estadisticas:
            mostrar_kpis_promotor(estadisticas, grupo_seleccionado)
        
        st.markdown("---")
        
        # Pestañas para diferentes visualizaciones - ORDEN CORREGIDO
        tab1, tab2, tab3 = st.tabs(["📈 Análisis del Grupo", "📋 Reporte Completo", "🏆 Ranking General"])
        
        with tab1:
    if estadisticas:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de distribución
            fig_distribucion = crear_grafico_distribucion(estadisticas, es_distrito=False)
            st.plotly_chart(fig_distribucion, use_container_width=True)
        
        with col2:
            # Mostrar desglose detallado
            st.markdown("#### 🟩 Desglose de Ingresos")
            
            datos_ingresos = {
                'Concepto': ['Ahorros', 'Actividades', 'Multas', 'Pagos Préstamos'],
                'Monto': [
                    estadisticas['ingresos']['ahorros'],
                    estadisticas['ingresos']['actividades'],
                    estadisticas['ingresos']['multas'],
                    estadisticas['ingresos']['pagos_prestamos']
                ]
            }
            
            df_ingresos = pd.DataFrame(datos_ingresos)
            df_ingresos['Monto'] = df_ingresos['Monto'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_ingresos, use_container_width=True, hide_index=True)
    else:
        st.info("📊 No hay datos del grupo seleccionado para mostrar.")

with tab2:  # Ahora esta es "Reporte Completo"
    if estadisticas:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🟩 Entradas de Dinero")
            st.write(f"**Ahorros:** ${estadisticas['ingresos']['ahorros']:,.2f}")
            st.write(f"**Actividades:** ${estadisticas['ingresos']['actividades']:,.2f}")
            st.write(f"**Multas:** ${estadisticas['ingresos']['multas']:,.2f}")
            st.write(f"**Pagos Préstamos:** ${estadisticas['ingresos']['pagos_prestamos']:,.2f}")
            st.markdown(f"**💰 Total Ingresos:** ${estadisticas['ingresos']['total']:,.2f}")
        
        with col2:
            st.markdown("#### 🟥 Salidas de Dinero")
            st.write(f"**Retiros:** ${estadisticas['egresos']['retiros']:,.2f}")
            st.write(f"**Desembolsos:** ${estadisticas['egresos']['desembolsos']:,.2f}")
            st.markdown(f"**💸 Total Egresos:** ${estadisticas['egresos']['total']:,.2f}")
            st.markdown(f"**🏦 Saldo Neto:** ${estadisticas['saldo_neto']:,.2f}")
    else:
        st.info("📋 No hay datos del grupo seleccionado para mostrar el reporte completo.")

with tab3:  # Ahora esta es "Ranking General"
    if ranking_grupos:
        # Gráfico de ranking
        fig_ranking = crear_grafico_ranking_grupos(ranking_grupos)
        if fig_ranking:
            st.plotly_chart(fig_ranking, use_container_width=True)
        
        # Tabla de ranking completa
        with st.expander("📋 Ver ranking completo de grupos"):
            df_ranking = pd.DataFrame(ranking_grupos)
            df_ranking['Posición'] = range(1, len(df_ranking) + 1)
            
            # Reordenar columnas
            columnas = ['Posición', 'nombre_grupo', 'distrito', 'ingresos_total', 'ahorros_actividades', 'multas', 'pagos_prestamos']
            df_display = df_ranking[columnas].copy()
            df_display.columns = ['Posición', 'Grupo', 'Distrito', 'Ingresos Total', 'Ahorros/Actividades', 'Multas', 'Pagos Préstamos']
            
            # Formatear números
            columnas_monetarias = ['Ingresos Total', 'Ahorros/Actividades', 'Multas', 'Pagos Préstamos']
            for col in columnas_monetarias:
                df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("🏆 No hay datos de grupos para mostrar el ranking.")

def mostrar_reporte_institucional(fecha_inicio, fecha_fin):
    """Muestra el reporte para usuario institucional con diseño mejorado"""
    
    # Obtener estadísticas por distrito
    estadisticas_distritos = obtener_estadisticas_por_distrito(fecha_inicio, fecha_fin)
    
    if not estadisticas_distritos:
        st.warning("No se encontraron datos para el período seleccionado.")
        return
    
    # Título principal
    st.markdown("### 📊 Métricas por Distrito")
    
    # SELECTOR DE DISTRITOS INMEDIATAMENTE DESPUÉS DEL TÍTULO
    # Crear lista de distritos disponibles
    distritos_disponibles = ["Todos"] + [stats['distrito'] for stats in estadisticas_distritos]
    
    # Selectbox para filtrar por distrito
    distrito_seleccionado = st.selectbox(
        "📍 Seleccione un distrito:",
        options=distritos_disponibles,
        help="Seleccione 'Todos' para ver todos los distritos",
        key="selector_distrito"
    )
    
    # Filtrar datos según el distrito seleccionado
    if distrito_seleccionado == "Todos":
        datos_filtrados = estadisticas_distritos
        # Calcular totales generales
        total_ingresos = sum(stats['ingresos']['total'] for stats in estadisticas_distritos)
        total_egresos = sum(stats['egresos']['total'] for stats in estadisticas_distritos)
        total_saldo = total_ingresos - total_egresos
    else:
        datos_filtrados = [stats for stats in estadisticas_distritos if stats['distrito'] == distrito_seleccionado]
        if datos_filtrados:
            stats = datos_filtrados[0]
            total_ingresos = stats['ingresos']['total']
            total_egresos = stats['egresos']['total']
            total_saldo = stats['saldo_neto']
        else:
            total_ingresos = 0
            total_egresos = 0
            total_saldo = 0
    
    # MOSTRAR LOS KPIs CON LOS VALORES DEL DISTRITO SELECCIONADO
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💰 Ingresos Totales", 
            f"${total_ingresos:,.2f}",
            help="Suma de todos los ingresos" + (" del distrito seleccionado" if distrito_seleccionado != "Todos" else " de todos los distritos")
        )
    
    with col2:
        st.metric(
            "💸 Egresos Totales", 
            f"${total_egresos:,.2f}",
            help="Suma de todos los egresos" + (" del distrito seleccionado" if distrito_seleccionado != "Todos" else " de todos los distritos"),
            delta=f"-${total_egresos:,.2f}",
            delta_color="inverse"
        )
    
    with col3:
        color_saldo = "normal" if total_saldo >= 0 else "inverse"
        st.metric(
            "🏦 Saldo Neto Total", 
            f"${total_saldo:,.2f}",
            help="Saldo neto (Ingresos - Egresos)" + (" del distrito seleccionado" if distrito_seleccionado != "Todos" else " de todos los distritos"),
            delta=f"{total_saldo:,.2f}",
            delta_color=color_saldo
        )
    
    st.markdown("---")
    
    # Pestañas para diferentes visualizaciones
    tab1, tab2 = st.tabs(["📈 Tendencias por Distrito", "📋 Resumen Detallado"])
    
    with tab1:
        if datos_filtrados:
            # Gráfico de tendencias
            fig_tendencias = crear_grafico_tendencias_distritos(datos_filtrados)
            titulo_grafico = f'📈 Tendencias Financieras - {distrito_seleccionado}' if distrito_seleccionado != "Todos" else '📈 Tendencias Financieras por Distrito'
            fig_tendencias.update_layout(
                title=dict(
                    text=titulo_grafico,
                    font=dict(size=20, color='#4C3A60')
                )
            )
            st.plotly_chart(fig_tendencias, use_container_width=True)
            
            # Gráfico de distribución
            col1, col2 = st.columns(2)
            with col1:
                fig_distribucion = crear_grafico_distribucion(datos_filtrados, es_distrito=True)
                titulo_distribucion = f'🥧 Distribución de Ingresos - {distrito_seleccionado}' if distrito_seleccionado != "Todos" else '🥧 Distribución de Ingresos por Distrito'
                fig_distribucion.update_layout(
                    title=dict(
                        text=titulo_distribucion,
                        font=dict(size=16, color='#4C3A60')
                    )
                )
                st.plotly_chart(fig_distribucion, use_container_width=True)
        else:
            st.info("📊 No hay datos para el distrito seleccionado.")
    
    with tab2:
        if datos_filtrados:
            # Crear DataFrame consolidado
            datos_consolidados = []
            for stats in datos_filtrados:
                datos_consolidados.append({
                    'Distrito': stats['distrito'],
                    'Ingresos': stats['ingresos']['total'],
                    'Egresos': stats['egresos']['total'],
                    'Saldo Neto': stats['saldo_neto']
                })
            
            df_consolidado = pd.DataFrame(datos_consolidados)
            
            # Formatear columnas monetarias
            df_display = df_consolidado.copy()
            df_display['Ingresos'] = df_display['Ingresos'].apply(lambda x: f"${x:,.2f}")
            df_display['Egresos'] = df_display['Egresos'].apply(lambda x: f"${x:,.2f}")
            df_display['Saldo Neto'] = df_display['Saldo Neto'].apply(lambda x: f"${x:,.2f}")
            
            titulo_resumen = f"### 📋 Resumen - {distrito_seleccionado}" if distrito_seleccionado != "Todos" else "### 📋 Resumen General por Distrito"
            st.markdown(titulo_resumen)
            st.dataframe(df_display, use_container_width=True)
            
            # Mostrar detalles expandibles por distrito
            if distrito_seleccionado == "Todos":
                st.markdown("### 📊 Detalles por Distrito")
                col1, col2 = st.columns(2)
                with col1:
                    for stats in datos_filtrados:
                        with st.expander(f"📁 {stats['distrito']}"):
                            st.write(f"**Ingresos:** ${stats['ingresos']['total']:,.2f}")
                            st.write(f"**Egresos:** ${stats['egresos']['total']:,.2f}")
                            st.write(f"**Saldo Neto:** ${stats['saldo_neto']:,.2f}")
        else:
            st.info("📋 No hay datos para el distrito seleccionado.")

def vista_reportes():
    """
    Módulo de Reportes - Dashboard financiero mejorado
    """
    # ===============================
    # 0. Verificar acceso y permisos
    # ===============================
    rol = st.session_state.get("rol", "").lower()
    usuario = st.session_state.get("usuario", "").lower()
    id_grupo = st.session_state.get("id_grupo")

    # ✅ CORREGIDO: Promotores e institucionales no necesitan grupo asignado
    if rol not in ["promotor", "institucional"] and usuario != "dark":
        st.error("❌ No tiene permisos para acceder a este módulo.")
        return

    # ✅ CORREGIDO: Solo miembros necesitan grupo asignado
    if rol == "miembro" and not id_grupo:
        st.error("❌ No tiene un grupo asignado. Contacte al administrador.")
        return

    # Título principal con diseño mejorado
    st.markdown("""
    <div style='text-align: center;'>
        <h1>📊 Dashboard de Reportes Financieros</h1>
        <h3 style='color: #4C3A60; margin-top: -10px;'>Análisis completo de ingresos y egresos</h3>
    </div>
    """, unsafe_allow_html=True)

    # ===============================
    # 1. FILTROS PRINCIPALES
    # ===============================
    st.subheader("🎛️ Configurar Período de Análisis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_inicio = st.date_input(
            "📅 Fecha inicio", 
            date.today() - timedelta(days=30),
            key="fecha_inicio_reportes"
        )
    
    with col2:
        fecha_fin = st.date_input(
            "📅 Fecha fin", 
            date.today(),
            key="fecha_fin_reportes"
        )
    
    # Validar fechas
    if fecha_inicio > fecha_fin:
        st.error("❌ La fecha de inicio no puede ser mayor que la fecha fin")
        return

    st.markdown("---")

    # ===============================
    # 2. MOSTRAR REPORTES SEGÚN ROL
    # ===============================
    if rol == "promotor":
        # Promotor: puede seleccionar grupo individual y ver ranking
        mostrar_reporte_promotor(fecha_inicio, fecha_fin)
        
    elif rol == "institucional" or usuario == "dark":
        # Institucional: ve estadísticas por distrito
        mostrar_reporte_institucional(fecha_inicio, fecha_fin)

    # ===============================
    # 3. INFORMACIÓN DEL PERÍODO EN SIDEBAR
    # ===============================
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **📅 Período Analizado:**
    - Inicio: {fecha_inicio}
    - Fin: {fecha_fin}
    - Rol: {rol.title()}
    """)

    # ===============================
    # 4. BOTÓN REGRESAR
    # ===============================
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⬅️ Regresar al Menú Principal", use_container_width=True):
            st.session_state.page = "menu"
            st.rerun()
