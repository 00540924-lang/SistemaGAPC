import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt

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
        
        # Mostrar desglose detallado (el mismo código que antes)
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
            
            # Gráfico de torta para ingresos (código igual al anterior)
            if estadisticas['ingresos']['total'] > 0:
                fig, ax = plt.subplots(figsize=(8, 6))
                conceptos = ['Multas', 'Ahorros', 'Actividades', 'Pagos Préstamos']
                montos = [
                    estadisticas['ingresos']['multas'],
                    estadisticas['ingresos']['ahorros'],
                    estadisticas['ingresos']['actividades'],
                    estadisticas['ingresos']['pagos_prestamos']
                ]
                
                # Filtrar conceptos con montos mayores a 0
                conceptos_filtrados = []
                montos_filtrados = []
                for concepto, monto in zip(conceptos, montos):
                    if monto > 0:
                        conceptos_filtrados.append(concepto)
                        montos_filtrados.append(monto)
                
                if montos_filtrados:
                    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
                    wedges, texts, autotexts = ax.pie(
                        montos_filtrados, 
                        labels=conceptos_filtrados, 
                        autopct='%1.1f%%',
                        colors=colors[:len(montos_filtrados)],
                        startangle=90
                    )
                    
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                    
                    ax.set_title('Distribución de Ingresos', fontweight='bold', pad=20)
                    st.pyplot(fig)
        
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
            
            # Gráfico de torta para egresos (código igual al anterior)
            if estadisticas['egresos']['total'] > 0:
                fig, ax = plt.subplots(figsize=(8, 6))
                conceptos = ['Retiros', 'Desembolsos']
                montos = [
                    estadisticas['egresos']['retiros'],
                    estadisticas['egresos']['desembolsos']
                ]
                
                # Filtrar conceptos con montos mayores a 0
                conceptos_filtrados = []
                montos_filtrados = []
                for concepto, monto in zip(conceptos, montos):
                    if monto > 0:
                        conceptos_filtrados.append(concepto)
                        montos_filtrados.append(monto)
                
                if montos_filtrados:
                    colors = ['#FFA726', '#AB47BC']
                    wedges, texts, autotexts = ax.pie(
                        montos_filtrados, 
                        labels=conceptos_filtrados, 
                        autopct='%1.1f%%',
                        colors=colors[:len(montos_filtrados)],
                        startangle=90
                    )
                    
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                    
                    ax.set_title('Distribución de Egresos', fontweight='bold', pad=20)
                    st.pyplot(fig)

def mostrar_reporte_institucional(fecha_inicio, fecha_fin):
    """Muestra el reporte para usuario institucional (todos los grupos)"""
    st.subheader("🏢 Reporte Institucional - Todos los Grupos")
    
    # Obtener todos los grupos
    grupos = obtener_todos_los_grupos()
    
    if not grupos:
        st.warning("No se encontraron grupos en el sistema.")
        return
    
    # Obtener estadísticas para cada grupo
    estadisticas_grupos = []
    for id_grupo, nombre_grupo in grupos:
        estadisticas = obtener_estadisticas_por_grupo(id_grupo, fecha_inicio, fecha_fin)
        if estadisticas:
            estadisticas['nombre_grupo'] = nombre_grupo
            estadisticas_grupos.append(estadisticas)
    
    if not estadisticas_grupos:
        st.warning("No se encontraron datos para el período seleccionado.")
        return
    
    # Crear DataFrame consolidado
    datos_consolidados = []
    for stats in estadisticas_grupos:
        datos_consolidados.append({
            'Grupo': stats['nombre_grupo'],
            'Total Ingresos': stats['ingresos']['total'],
            'Total Egresos': stats['egresos']['total'],
            'Saldo Neto': stats['saldo_neto']
        })
    
    df_consolidado = pd.DataFrame(datos_consolidados)
    
    # Mostrar tabla consolidada
    st.markdown("### 📋 Resumen por Grupo")
    
    # Formatear columnas monetarias
    df_display = df_consolidado.copy()
    df_display['Total Ingresos'] = df_display['Total Ingresos'].apply(lambda x: f"${x:,.2f}")
    df_display['Total Egresos'] = df_display['Total Egresos'].apply(lambda x: f"${x:,.2f}")
    df_display['Saldo Neto'] = df_display['Saldo Neto'].apply(lambda x: f"${x:,.2f}")
    
    st.dataframe(df_display, use_container_width=True)
    
    # Mostrar totales generales
    st.write("---")
    st.markdown("### 📊 Totales Generales")
    
    total_ingresos = sum(stats['ingresos']['total'] for stats in estadisticas_grupos)
    total_egresos = sum(stats['egresos']['total'] for stats in estadisticas_grupos)
    total_saldo = total_ingresos - total_egresos
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Total Ingresos General", f"${total_ingresos:,.2f}")
    
    with col2:
        st.metric("💸 Total Egresos General", f"${total_egresos:,.2f}")
    
    with col3:
        color_saldo = "normal" if total_saldo >= 0 else "inverse"
        st.metric("🏦 Saldo Neto General", f"${total_saldo:,.2f}", delta_color=color_saldo)
    
    # Gráfico de barras comparativo
    st.write("---")
    st.markdown("### 📈 Comparativa entre Grupos")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Gráfico de ingresos por grupo
    grupos_nombres = [stats['nombre_grupo'] for stats in estadisticas_grupos]
    ingresos = [stats['ingresos']['total'] for stats in estadisticas_grupos]
    egresos = [stats['egresos']['total'] for stats in estadisticas_grupos]
    
    bars1 = ax1.bar(grupos_nombres, ingresos, color='#4CAF50', alpha=0.7, label='Ingresos')
    ax1.set_title('Ingresos por Grupo', fontweight='bold', pad=20)
    ax1.set_ylabel('Monto ($)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Agregar valores en las barras
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}', ha='center', va='bottom', fontweight='bold')
    
    # Gráfico de egresos por grupo
    bars2 = ax2.bar(grupos_nombres, egresos, color='#F44336', alpha=0.7, label='Egresos')
    ax2.set_title('Egresos por Grupo', fontweight='bold', pad=20)
    ax2.set_ylabel('Monto ($)')
    ax2.tick_params(axis='x', rotation=45)
    
    # Agregar valores en las barras
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig)

def vista_reportes():
    """
    Módulo de Reportes - Estadísticas financieras por grupo
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
        # ✅ CORREGIDO: Promotor ve todos los grupos que supervisa
        mostrar_reporte_institucional(fecha_inicio, fecha_fin)
        
    elif rol == "institucional" or usuario == "dark":
        # Institucional: ve todos los grupos
        mostrar_reporte_institucional(fecha_inicio, fecha_fin)

    # ===============================
    # 3. Botón regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
