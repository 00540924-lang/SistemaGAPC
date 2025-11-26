import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def obtener_datos_cierre_ciclo(id_grupo, fecha_inicio, fecha_fin):
    """
    Obtiene todos los datos necesarios para el cierre de ciclo con la nueva lógica
    """
    try:
        conn = obtener_conexion()
        if not conn:
            st.error("❌ No se pudo conectar a la base de datos")
            return None
            
        cursor = conn.cursor(dictionary=True)
        
        # 1. Obtener información básica del grupo
        cursor.execute("""
            SELECT id_grupo, Nombre_grupo, distrito 
            FROM Grupos 
            WHERE id_grupo = %s
        """, (id_grupo,))
        grupo_info = cursor.fetchone()
        
        if not grupo_info:
            st.error("❌ No se encontró el grupo especificado")
            conn.close()
            return None
        
        # 2. Obtener miembros del grupo
        cursor.execute("""
            SELECT M.id_miembro, M.Nombre
            FROM Miembros M
            JOIN Grupomiembros GM ON M.id_miembro = GM.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY M.Nombre
        """, (id_grupo,))
        miembros = cursor.fetchall()
        
        # 3. Obtener TOTALES GRUPALES (para dividir entre todos)
        # 3.1 Total de multas pagadas del grupo
        cursor.execute("""
            SELECT COALESCE(SUM(MT.monto_a_pagar), 0) as total_multas
            FROM Multas MT
            JOIN Miembros M ON MT.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            AND MT.fecha BETWEEN %s AND %s
            AND MT.pagada = 1
        """, (id_grupo, fecha_inicio, fecha_fin))
        resultado_multas = cursor.fetchone()
        total_multas_grupo = float(resultado_multas['total_multas'])
        
        # 3.2 Total de intereses de préstamos pagados del grupo
        cursor.execute("""
            SELECT COALESCE(SUM(PP.interes), 0) as total_intereses
            FROM prestamo_pagos PP
            JOIN prestamos P ON PP.id_prestamo = P.id_prestamo
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s 
            AND PP.fecha BETWEEN %s AND %s
            AND PP.estado = 'pagado'
        """, (id_grupo, fecha_inicio, fecha_fin))
        resultado_intereses = cursor.fetchone()
        total_intereses_grupo = float(resultado_intereses['total_intereses'])
        
        # 3.3 Total de actividades del grupo
        cursor.execute("""
            SELECT COALESCE(SUM(actividades), 0) as total_actividades
            FROM ahorro_final 
            WHERE id_grupo = %s 
            AND fecha_registro BETWEEN %s AND %s
        """, (id_grupo, fecha_inicio, fecha_fin))
        resultado_actividades = cursor.fetchone()
        total_actividades_grupo = float(resultado_actividades['total_actividades'])
        
        # 4. Calcular FONDO GRUPAL TOTAL (lo que se divide entre todos)
        fondo_grupal_total = total_multas_grupo + total_intereses_grupo + total_actividades_grupo
        
        # 5. Calcular lo que le corresponde a CADA socia
        num_miembros = len(miembros)
        monto_por_socia = fondo_grupal_total / num_miembros if num_miembros > 0 else 0
        
        # 6. Obtener ahorros individuales de cada socia
        datos_cierre = []
        total_ahorro_grupo = 0
        
        for miembro in miembros:
            # Saldo de ahorros individual (solo lo que ahorró, sin retiros)
            cursor.execute("""
                SELECT COALESCE(SUM(ahorros), 0) as total_ahorros
                FROM ahorro_final 
                WHERE id_grupo = %s AND id_miembro = %s
                AND fecha_registro BETWEEN %s AND %s
            """, (id_grupo, miembro['id_miembro'], fecha_inicio, fecha_fin))
            resultado_ahorro = cursor.fetchone()
            total_ahorros = float(resultado_ahorro['total_ahorros'])
            
            # Lo que le corresponde del fondo grupal
            monto_fondo_socia = monto_por_socia
            
            # Total a entregar a la socia
            total_a_entregar = total_ahorros + monto_fondo_socia
            
            datos_cierre.append({
                'id_miembro': miembro['id_miembro'],
                'nombre_completo': miembro['Nombre'],
                'ahorros_individuales': total_ahorros,
                'monto_fondo_grupal': monto_fondo_socia,
                'total_a_entregar': total_a_entregar,
                'entregado': False  # Para marcar cuando se entregue
            })
            
            total_ahorro_grupo += total_ahorros
        
        conn.close()
        
        return {
            'grupo_info': grupo_info,
            'miembros': datos_cierre,
            'totales_grupales': {
                'total_multas': total_multas_grupo,
                'total_intereses': total_intereses_grupo,
                'total_actividades': total_actividades_grupo,
                'fondo_grupal_total': fondo_grupal_total,
                'total_ahorro_grupo': total_ahorro_grupo,
                'num_miembros': num_miembros,
                'monto_por_socia': monto_por_socia
            },
            'fechas': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
        }
        
    except Exception as e:
        st.error(f"❌ Error al obtener datos para cierre de ciclo: {str(e)}")
        return None

def mostrar_resumen_cierre(datos_cierre):
    """
    Muestra un resumen visual del cierre de ciclo con la nueva lógica
    """
    st.markdown("### 📊 Resumen del Cierre de Ciclo")
    
    # Mostrar intervalo de fechas de forma segura
    col_fechas = st.columns(2)
    with col_fechas[0]:
        # Usar get() para evitar KeyError
        fecha_inicio = datos_cierre.get('fechas', {}).get('fecha_inicio', 'No disponible')
        st.info(f"**Fecha de inicio:** {fecha_inicio}")
    
    with col_fechas[1]:
        fecha_fin = datos_cierre.get('fechas', {}).get('fecha_fin', 'No disponible')
        st.info(f"**Fecha de cierre:** {fecha_fin}")
    
    # KPIs principales - usar get() para evitar errores
    totales = datos_cierre.get('totales_grupales', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "👥 Total Miembros",
            totales.get('num_miembros', 0),
            help="Número de miembros en el grupo"
        )
    
    with col2:
        st.metric(
            "💰 Total Ahorros del Grupo",
            f"${totales.get('total_ahorro_grupo', 0):,.2f}",
            help="Suma de ahorros individuales de todas las socias"
        )
    
    with col3:
        st.metric(
            "🏦 Fondo Grupal a Repartir",
            f"${totales.get('fondo_grupal_total', 0):,.2f}",
            help="Multas + Intereses + Actividades"
        )
    
    # Desglose del fondo grupal
    st.markdown("---")
    st.subheader("🥧 Composición del Fondo Grupal")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💰 Multas",
            f"${totales.get('total_multas', 0):,.2f}"
        )
    
    with col2:
        st.metric(
            "💸 Intereses Préstamos",
            f"${totales.get('total_intereses', 0):,.2f}"
        )
    
    with col3:
        st.metric(
            "📊 Actividades",
            f"${totales.get('total_actividades', 0):,.2f}"
        )
    
    # Gráfico de distribución del fondo grupal
    labels = ['Multas', 'Intereses', 'Actividades']
    values = [
        totales.get('total_multas', 0),
        totales.get('total_intereses', 0),
        totales.get('total_actividades', 0)
    ]
    
    # Solo mostrar gráfico si hay datos
    if sum(values) > 0:
        fig = px.pie(
            values=values,
            names=labels,
            title='Distribución del Fondo Grupal',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar en el gráfico de distribución del fondo grupal.")

def mostrar_formulario_cierre(datos_cierre):
    """
    Muestra el formulario de cierre de ciclo con la nueva lógica
    """
    st.markdown("---")
    st.markdown("### 📋 Liquidación por Socia")
    
    # Usar get() para evitar errores
    grupo_info = datos_cierre.get('grupo_info', {})
    totales = datos_cierre.get('totales_grupales', {})
    fechas = datos_cierre.get('fechas', {})
    
    st.markdown(f"**Grupo:** {grupo_info.get('Nombre_grupo', 'No disponible')} | **Distrito:** {grupo_info.get('distrito', 'No disponible')}")
    st.markdown(f"**Período:** {fechas.get('fecha_inicio', 'No disponible')} al {fechas.get('fecha_fin', 'No disponible')}")
    st.info(f"💡 **Monto por socia del fondo grupal:** ${totales.get('monto_por_socia', 0):,.2f}")
    
    # Crear DataFrame para mostrar
    datos_liquidacion = []
    miembros = datos_cierre.get('miembros', [])
    
    for i, socia in enumerate(miembros):
        datos_liquidacion.append({
            'Nº': i + 1,
            'Socia': socia.get('nombre_completo', 'No disponible'),
            'Ahorros Individuales': f"${socia.get('ahorros_individuales', 0):,.2f}",
            'Parte Fondo Grupal': f"${socia.get('monto_fondo_grupal', 0):,.2f}",
            'Total a Entregar': f"${socia.get('total_a_entregar', 0):,.2f}",
            'Entregado': '✅ Sí' if socia.get('entregado', False) else '❌ No'
        })
    
    df = pd.DataFrame(datos_liquidacion)
    st.dataframe(df, use_container_width=True)
    
    # Sección para marcar entregas
    st.markdown("#### ✅ Confirmar Entregas")
    st.warning("Marque cada socia como entregada una vez que reciba su dinero.")
    
    for i, socia in enumerate(miembros):
        col_socia1, col_socia2, col_socia3 = st.columns([3, 2, 1])
        
        with col_socia1:
            st.write(f"**{socia.get('nombre_completo', 'No disponible')}**")
            st.write(f"Ahorros: ${socia.get('ahorros_individuales', 0):,.2f} + Fondo: ${socia.get('monto_fondo_grupal', 0):,.2f}")
            st.write(f"**Total: ${socia.get('total_a_entregar', 0):,.2f}**")
        
        with col_socia2:
            entregado = st.checkbox(
                "Dinero entregado",
                value=socia.get('entregado', False),
                key=f"entregado_checkbox_{i}"
            )
            datos_cierre['miembros'][i]['entregado'] = entregado
        
        with col_socia3:
            if entregado:
                st.success("✅ Entregado")
            else:
                st.error("⏳ Pendiente")
    
    return datos_cierre

def validar_cierre_ciclo(datos_cierre):
    """
    Valida que el cierre esté listo para ejecutar
    """
    errores = []
    
    if not datos_cierre or not datos_cierre.get('miembros'):
        errores.append("No hay miembros en el grupo")
        return errores
    
    # Verificar que todas las socias estén marcadas como entregadas
    socias_pendientes = [
        socia.get('nombre_completo', 'Socia sin nombre') 
        for socia in datos_cierre['miembros'] 
        if not socia.get('entregado', False)
    ]
    
    if socias_pendientes:
        errores.append(f"Socias pendientes de entrega: {', '.join(socias_pendientes)}")
    
    return errores

def vista_cierre_ciclo():
    """
    Módulo de Cierre de Ciclo - Dashboard principal
    """
    # Verificar permisos - Solo miembros pueden acceder
    rol = st.session_state.get("rol", "").lower()
    usuario = st.session_state.get("usuario", "")
    id_grupo = st.session_state.get("id_grupo")
    
    # SOLO MIEMBROS pueden acceder
    if rol != "miembro":
        st.error("❌ No tiene permisos para acceder a este módulo. Solo los miembros pueden realizar cierres de ciclo.")
        return
    
    # Verificar que el miembro tenga grupo asignado
    if not id_grupo:
        st.error("⚠️ No se encontró el grupo del usuario. Contacte al administrador.")
        return
    
    st.markdown("""
    <div style='text-align: center;'>
        <h1>📅 Cierre de Ciclo</h1>
        <h3 style='color: #4C3A60; margin-top: -10px;'>Proceso de cierre financiero del ciclo grupal</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # ===============================
    # 1. CONFIGURACIÓN INICIAL
    # ===============================
    st.subheader("🎛️ Configuración del Cierre")
    
    # Usar claves únicas para evitar conflictos
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        # Para miembros, usar su grupo asignado automáticamente
        id_grupo_seleccionado = id_grupo
        grupo_seleccionado = obtener_nombre_grupo(id_grupo)
        st.info(f"**Grupo asignado:** {grupo_seleccionado}")
    
    with col_config2:
        # Calcular fechas por defecto (últimos 6 meses para tener más datos)
        hoy = date.today()
        primer_dia_mes_actual = date(hoy.year, hoy.month, 1)
        fecha_fin_default = primer_dia_mes_actual - timedelta(days=1)  # Último día del mes anterior
        fecha_inicio_default = fecha_fin_default - timedelta(days=180)  # 6 meses atrás
        
        fecha_inicio = st.date_input(
            "📅 Fecha de inicio del ciclo",
            fecha_inicio_default,
            key="cierre_fecha_inicio"
        )
        
        fecha_fin = st.date_input(
            "📅 Fecha de cierre del ciclo",
            fecha_fin_default,
            key="cierre_fecha_fin"
        )
        
        # Validar que la fecha de inicio sea anterior a la fecha de fin
        if fecha_inicio >= fecha_fin:
            st.error("❌ La fecha de inicio debe ser anterior a la fecha de cierre")
    
    # ===============================
    # 2. OBTENER Y MOSTRAR DATOS
    # ===============================
    if st.button("🔄 Cargar Datos para Cierre", type="primary", key="btn_cargar_datos"):
        if fecha_inicio >= fecha_fin:
            st.error("❌ Por favor, corrija las fechas antes de continuar")
        else:
            with st.spinner("Cargando datos del ciclo..."):
                datos_cierre = obtener_datos_cierre_ciclo(id_grupo_seleccionado, fecha_inicio, fecha_fin)
                
                if datos_cierre:
                    # Usar un diccionario temporal en lugar de session_state
                    st.session_state.cierre_info = {
                        'datos': datos_cierre,
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'grupo': id_grupo_seleccionado
                    }
                    st.success("✅ Datos cargados exitosamente")
                else:
                    st.error("❌ No se pudieron cargar los datos para el cierre")
    
    # ===============================
    # 3. PROCESAR CIERRE SI HAY DATOS
    # ===============================
    if 'cierre_info' in st.session_state:
        datos_cierre = st.session_state.cierre_info['datos']
        
        # Mostrar resumen
        mostrar_resumen_cierre(datos_cierre)
        
        # Mostrar formulario editable
        datos_cierre_actualizado = mostrar_formulario_cierre(datos_cierre)
        
        # Botón para validar cierre
        st.markdown("---")
        st.subheader("✅ Validar Cierre")
        
        if st.button("🔍 Validar Cierre", type="primary", use_container_width=True, key="btn_validar_cierre"):
            errores = validar_cierre_ciclo(datos_cierre_actualizado)
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                st.success("✅ Validación exitosa. Todas las socias han sido marcadas como entregadas.")
    
    # ===============================
    # 4. BOTÓN REGRESAR
    # ===============================
    st.markdown("---")
    if st.button("⬅️ Regresar al Menú Principal", key="btn_regresar_cierre"):
        st.session_state.page = "menu"
        st.rerun()

# Funciones auxiliares que estaban en tu código original
def obtener_todos_los_grupos():
    """Obtiene todos los grupos disponibles"""
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
