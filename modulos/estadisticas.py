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
        
        # Construir condiciones WHERE dinámicas
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
        
        # Consulta principal para estadísticas
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
                
                -- Estadísticas de préstamos
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
            # Calcular saldo neto correctamente
            estadisticas['saldo_neto'] = (
                estadisticas['total_ahorros'] + 
                estadisticas['total_actividades'] - 
                estadisticas['total_retiros']
            )
            
            # Calcular total egresos
            estadisticas['total_egresos'] = (
                estadisticas['total_retiros'] + 
                estadisticas['prestamos_activos']
            )
        
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
        
        # Construir condiciones WHERE dinámicas
        condiciones = ["GM.id_grupo = %s"]
        params = [id_grupo]
        
        if fecha_inicio and fecha_fin:
            condiciones.append("(AF.fecha_registro BETWEEN %s AND %s OR MT.fecha BETWEEN %s AND %s)")
            params.extend([fecha_inicio, fecha_fin] * 2)
        
        where_clause = " AND ".join(condiciones)
        
        query = f"""
            SELECT 
                M.id_miembro,
                M.Nombre,
                
                -- Ahorros del miembro
                COALESCE(SUM(AF.ahorros), 0) as total_ahorros,
                COALESCE(SUM(AF.actividades), 0) as total_actividades,
                COALESCE(SUM(AF.retiros), 0) as total_retiros,
                COALESCE(SUM(AF.saldo_final), 0) as saldo_ahorro,
                
                -- Multas del miembro
                COALESCE(SUM(MT.monto_a_pagar), 0) as total_multas,
                COUNT(DISTINCT CASE WHEN MT.pagada = 1 THEN MT.id_multa END) as multas_pagadas,
                COUNT(DISTINCT CASE WHEN MT.pagada = 0 THEN MT.id_multa END) as multas_pendientes
                
            FROM Miembros M
            JOIN Grupomiembros GM ON M.id_miembro = GM.id_miembro
            LEFT JOIN ahorro_final AF ON M.id_miembro = AF.id_miembro AND AF.id_grupo = GM.id_grupo
            LEFT JOIN Multas MT ON M.id_miembro = MT.id_miembro
            WHERE {where_clause}
            GROUP BY M.id_miembro, M.Nombre
            ORDER BY saldo_ahorro DESC
        """
        
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
        
    except Exception as e:
        st.error(f"Error al obtener estadísticas por miembro: {e}")
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
            condiciones.append("(AF.fecha_registro BETWEEN %s AND %s OR MT.fecha BETWEEN %s AND %s)")
            params.extend([fecha_inicio, fecha_fin] * 2)
        
        where_clause = " AND ".join(condiciones)
        
        query = f"""
            SELECT 
                -- Ahorros
                COALESCE(SUM(AF.ahorros), 0) as ahorros,
                COALESCE(SUM(AF.actividades), 0) as actividades,
                COALESCE(SUM(AF.retiros), 0) as retiros,
                
                -- Multas
                COALESCE(SUM(MT.monto_a_pagar), 0) as multas
                
            FROM Grupomiembros GM
            LEFT JOIN ahorro_final AF ON GM.id_miembro = AF.id_miembro AND AF.id_grupo = GM.id_grupo
            LEFT JOIN Multas MT ON GM.id_miembro = MT.id_miembro
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
        <h1>📊 Estadísticas</h1>
        <h3 style='color: #4C3A60; margin-top: -10px;'>Resumen completo del grupo</h3>
    </div>
    """, unsafe_allow_html=True)

    # ===============================
    # 1. FILTROS PRINCIPALES - CON NÚMERO DE MIEMBROS EN "TODOS"
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
        total_miembros = 0
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
                total_miembros = len(miembros)
                cursor.close()
            except:
                pass
            finally:
                if conn.is_connected():
                    conn.close()
        
        opciones_miembros = {m['id_miembro']: m['Nombre'] for m in miembros}
        
        # Crear opciones con "Todos (X)" donde X es el número de miembros
        opciones_formateadas = {
            "Todos": f"Todos ({total_miembros})"
        }
        for id_miembro, nombre in opciones_miembros.items():
            opciones_formateadas[id_miembro] = nombre
        
        miembro_filtro = st.selectbox(
            "👤 Filtrar por miembro:",
            options=["Todos"] + list(opciones_miembros.keys()),
            format_func=lambda x: opciones_formateadas[x],
            key="miembro_filtro"
        )

    # ===============================
    # 2. KPI PRINCIPALES - SIN MIEMBROS ACTIVOS
    # ===============================
    st.subheader("📈 Métricas Principales")
    
    # Obtener estadísticas
    id_miembro_filtro = None if miembro_filtro == "Todos" else miembro_filtro
    stats = obtener_estadisticas_grupo(id_grupo, fecha_inicio, fecha_fin, id_miembro_filtro)
    
    if stats:
        # SOLO 4 MÉTRICAS - SIN MIEMBROS ACTIVOS
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Saldo Total", 
                f"${stats.get('saldo_neto', 0):,.2f}",
                help="Saldo neto del grupo (ahorros + actividades - retiros)"
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
            st.metric(
                "📉 Total Egresos", 
                f"${stats.get('total_egresos', 0):,.2f}",
                help="Total de retiros y préstamos activos"
            )

    else:
        st.warning("No se pudieron cargar las estadísticas del grupo.")

    # ===============================
    # 3. GRÁFICOS Y VISUALIZACIONES
    # ===============================
    st.subheader("📊 Visualizaciones")
    
    tab1, tab2 = st.tabs(["🥧 Distribución", "👥 Ranking Miembros"])
    
    with tab1:
        # Gráfico de distribución
        distribucion = obtener_distribucion_por_tipo(id_grupo, fecha_inicio, fecha_fin)
        
        if distribucion and any(distribucion.values()):
            labels = ['Ahorros', 'Actividades', 'Multas']
            values = [
                distribucion.get('ahorros', 0),
                distribucion.get('actividades', 0),
                distribucion.get('multas', 0)
            ]
            
            # Filtrar categorías con valores > 0
            filtered_data = [(label, value) for label, value in zip(labels, values) if value > 0]
            if filtered_data:
                labels_filtered, values_filtered = zip(*filtered_data)
                
                fig_pie = px.pie(
                    names=labels_filtered, 
                    values=values_filtered,
                    title='Distribución de Fondos por Tipo',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("🥧 No hay datos suficientes para mostrar la distribución.")
        else:
            st.info("🥧 No hay datos de distribución para mostrar en el período seleccionado.")
    
    with tab2:
        # Ranking de miembros
        stats_miembros = obtener_estadisticas_por_miembro(id_grupo, fecha_inicio, fecha_fin)
        
        if stats_miembros:
            df_miembros = pd.DataFrame(stats_miembros)
            
            # Asegurar que la columna 'saldo_ahorro' sea numérica
            df_miembros['saldo_ahorro'] = pd.to_numeric(df_miembros['saldo_ahorro'], errors='coerce').fillna(0)
            
            # Filtrar miembros con saldo positivo y ordenar
            miembros_con_saldo = df_miembros[df_miembros['saldo_ahorro'] > 0]
            
            if not miembros_con_saldo.empty:
                # Tomar los top 10 o todos si hay menos de 10
                top_miembros = miembros_con_saldo.nlargest(min(10, len(miembros_con_saldo)), 'saldo_ahorro')
                
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
                st.info("💰 No hay miembros con saldo de ahorro positivo para mostrar en el ranking.")
            
            # Mostrar tabla completa
            with st.expander("📋 Ver tabla completa de miembros"):
                columnas_mostrar = ['Nombre', 'total_ahorros', 'total_actividades', 'total_retiros', 'saldo_ahorro', 'total_multas']
                nombres_columnas = ['Miembro', 'Ahorros', 'Actividades', 'Retiros', 'Saldo', 'Multas']
                
                df_display = df_miembros[columnas_mostrar].copy()
                df_display.columns = nombres_columnas
                
                # Formatear números
                for col in nombres_columnas[1:]:
                    df_display[col] = df_display[col].apply(lambda x: f"${float(x):,.2f}" if pd.notna(x) else "$0.00")
                
                st.dataframe(df_display, use_container_width=True)
        else:
            st.info("👥 No hay datos de miembros para mostrar.")

    # ===============================
    # 4. BOTÓN REGRESAR
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
    """)
