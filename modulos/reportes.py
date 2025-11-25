import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

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

def mostrar_reporte_promotor(fecha_inicio, fecha_fin):
    """Muestra el reporte para un promotor (puede seleccionar grupo)"""
    st.subheader("👨‍💼 Reporte del Promotor")
    
    # Obtener todos los grupos para que el promotor seleccione
    grupos = obtener_todos_los_grupos()
    
    if not grupos:
        st.warning("No se encontraron grupos en el sistema.")
        return
    
    # Crear lista de grupos para selección
    opciones_grupos = {f"{nombre} (ID: {id_grupo})": id_grupo for id_grupo, nombre in grupos}
    
    # Selectbox para elegir grupo
    grupo_seleccionado = st.selectbox(
        "Seleccione un grupo para ver reporte:",
        options=list(opciones_grupos.keys())
    )
    
    if grupo_seleccionado:
        id_grupo_seleccionado = opciones_grupos[grupo_seleccionado]
        
        # Obtener estadísticas del grupo seleccionado
        estadisticas = obtener_estadisticas_por_grupo(id_grupo_seleccionado, fecha_inicio, fecha_fin)
        
        if not estadisticas:
            st.warning("No se encontraron datos para el período seleccionado.")
            return
        
        # Mostrar métricas principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💰 Total Ingresos", 
                f"${estadisticas['ingresos']['total']:,.2f}",
                delta=f"${estadisticas['ingresos']['total']:,.2f}"
            )
        
        with col2:
            st.metric(
                "💸 Total Egresos", 
                f"${estadisticas['egresos']['total']:,.2f}",
                delta=f"-${estadisticas['egresos']['total']:,.2f}",
                delta_color="inverse"
            )
        
        with col3:
            color_saldo = "normal" if estadisticas['saldo_neto'] >= 0 else "inverse"
            st.metric(
                "🏦 Saldo Neto", 
                f"${estadisticas['saldo_neto']:,.2f}",
                delta=f"{estadisticas['saldo_neto']:,.2f}",
                delta_color=color_saldo
            )
        
        st.write("---")
        
        # Mostrar desglose detallado
        col_ingresos, col_egresos = st.columns(2)
        
        with col_ingresos:
            st.markdown("### 🟩 Desglose de Ingresos")
            
            datos_ingresos = {
                'Concepto': ['Multas', 'Ahorros', 'Actividades', 'Pagos de Préstamos'],
                'Monto': [
                    estadisticas['ingresos']['multas'],
                    estadisticas['ingresos']['ahorros'],
                    estadisticas['ingresos']['actividades'],
                    estadisticas['ingresos']['pagos_prestamos']
                ]
            }
            
            df_ingresos = pd.DataFrame(datos_ingresos)
            df_ingresos['Monto'] = df_ingresos['Monto'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_ingresos, use_container_width=True, hide_index=True)
            
        with col_egresos:
            st.markdown("### 🟥 Desglose de Egresos")
            
            datos_egresos = {
                'Concepto': ['Retiros de Ahorros', 'Desembolsos de Préstamos'],
                'Monto': [
                    estadisticas['egresos']['retiros'],
                    estadisticas['egresos']['desembolsos']
                ]
            }
            
            df_egresos = pd.DataFrame(datos_egresos)
            df_egresos['Monto'] = df_egresos['Monto'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_egresos, use_container_width=True, hide_index=True)

def mostrar_grafico_tendencias_distritos(estadisticas_distritos):
    """Muestra gráfico de líneas de tendencia para distritos"""
    
    # Crear DataFrame para el gráfico
    datos_grafico = []
    for stats in estadisticas_distritos:
        datos_grafico.append({
            'Distrito': stats['distrito'],
            'Ingresos': stats['ingresos']['total'],
            'Egresos': stats['egresos']['total'],
            'Saldo Neto': stats['saldo_neto']
        })
    
    df_grafico = pd.DataFrame(datos_grafico)
    
    # Ordenar por saldo neto (opcional)
    df_grafico = df_grafico.sort_values('Saldo Neto', ascending=False)
    
    # Crear gráfico de líneas de tendencia
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Preparar datos para el gráfico
    distritos = df_grafico['Distrito'].tolist()
    ingresos = df_grafico['Ingresos'].tolist()
    egresos = df_grafico['Egresos'].tolist()
    saldos = df_grafico['Saldo Neto'].tolist()
    
    # Crear índices para el eje X
    x = range(len(distritos))
    
    # Gráfico de líneas
    ax.plot(x, ingresos, marker='o', linewidth=3, markersize=8, label='Ingresos', color='#2E7D32')
    ax.plot(x, egresos, marker='s', linewidth=3, markersize=8, label='Egresos', color='#C62828')
    ax.plot(x, saldos, marker='^', linewidth=3, markersize=8, label='Saldo Neto', color='#1565C0')
    
    # Personalizar el gráfico
    ax.set_xlabel('Distritos', fontsize=12, fontweight='bold')
    ax.set_ylabel('Monto ($)', fontsize=12, fontweight='bold')
    ax.set_title('📈 Tendencias Financieras por Distrito', fontsize=16, fontweight='bold', pad=20)
    
    # Configurar eje X
    ax.set_xticks(x)
    ax.set_xticklabels(distritos, rotation=45, ha='right', fontsize=10)
    
    # Agregar grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Agregar leyenda
    ax.legend(loc='upper left', bbox_to_anchor=(0, 1), fontsize=11)
    
    # Agregar valores en los puntos
    for i, (ing, eg, sal) in enumerate(zip(ingresos, egresos, saldos)):
        ax.annotate(f'${ing:,.0f}', (i, ing), textcoords="offset points", 
                   xytext=(0,10), ha='center', fontsize=9, fontweight='bold', color='#2E7D32')
        ax.annotate(f'${eg:,.0f}', (i, eg), textcoords="offset points", 
                   xytext=(0,10), ha='center', fontsize=9, fontweight='bold', color='#C62828')
        ax.annotate(f'${sal:,.0f}', (i, sal), textcoords="offset points", 
                   xytext=(0,10), ha='center', fontsize=9, fontweight='bold', color='#1565C0')
    
    # Ajustar layout
    plt.tight_layout()
    
    # Mostrar gráfico
    st.pyplot(fig)

def mostrar_reporte_institucional(fecha_inicio, fecha_fin):
    """Muestra el reporte para usuario institucional (por distrito)"""
    
    # Obtener estadísticas por distrito
    estadisticas_distritos = obtener_estadisticas_por_distrito(fecha_inicio, fecha_fin)
    
    if not estadisticas_distritos:
        st.warning("No se encontraron datos para el período seleccionado.")
        return
    
    # Crear DataFrame consolidado por distrito
    datos_consolidados = []
    for stats in estadisticas_distritos:
        datos_consolidados.append({
            'Distrito': stats['distrito'],
            'Total Ingresos': stats['ingresos']['total'],
            'Total Egresos': stats['egresos']['total'],
            'Saldo Neto': stats['saldo_neto']
        })
    
    df_consolidado = pd.DataFrame(datos_consolidados)
    
    # Mostrar tabla consolidada
    st.markdown("### 📋 Resumen por Distrito")
    
    # Formatear columnas monetarias
    df_display = df_consolidado.copy()
    df_display['Total Ingresos'] = df_display['Total Ingresos'].apply(lambda x: f"${x:,.2f}")
    df_display['Total Egresos'] = df_display['Total Egresos'].apply(lambda x: f"${x:,.2f}")
    df_display['Saldo Neto'] = df_display['Saldo Neto'].apply(lambda x: f"${x:,.2f}")
    
    st.dataframe(df_display, use_container_width=True)
    
    # Mostrar totales generales
    st.write("---")
    st.markdown("### 📊 Totales Generales")
    
    total_ingresos = sum(stats['ingresos']['total'] for stats in estadisticas_distritos)
    total_egresos = sum(stats['egresos']['total'] for stats in estadisticas_distritos)
    total_saldo = total_ingresos - total_egresos
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Total Ingresos General", f"${total_ingresos:,.2f}")
    
    with col2:
        st.metric("💸 Total Egresos General", f"${total_egresos:,.2f}")
    
    with col3:
        color_saldo = "normal" if total_saldo >= 0 else "inverse"
        st.metric("🏦 Saldo Neto General", f"${total_saldo:,.2f}", delta_color=color_saldo)
    
    # Gráfico de líneas de tendencia por distrito
    st.write("---")
    st.markdown("### 📈 Tendencias Financieras por Distrito")
    
    mostrar_grafico_tendencias_distritos(estadisticas_distritos)

def vista_reportes():
    """
    Módulo de Reportes - Estadísticas financieras
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

    st.title("📊 Reportes Financieros")

    # ===============================
    # 1. FILTRO POR RANGO DE FECHAS
    # ===============================
    st.subheader("📅 Seleccionar Período")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_inicio = st.date_input(
            "Fecha inicio", 
            date.today() - timedelta(days=30),
            key="fecha_inicio_reportes"
        )
    
    with col2:
        fecha_fin = st.date_input(
            "Fecha fin", 
            date.today(),
            key="fecha_fin_reportes"
        )
    
    # Validar fechas
    if fecha_inicio > fecha_fin:
        st.error("❌ La fecha de inicio no puede ser mayor que la fecha fin")
        return

    st.write("---")

    # ===============================
    # 2. MOSTRAR REPORTES SEGÚN ROL
    # ===============================
    if rol == "promotor":
        # Promotor: puede seleccionar grupo individual
        mostrar_reporte_promotor(fecha_inicio, fecha_fin)
        
    elif rol == "institucional" or usuario == "dark":
        # Institucional: ve estadísticas por distrito
        mostrar_reporte_institucional(fecha_inicio, fecha_fin)

    # ===============================
    # 3. Botón regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
