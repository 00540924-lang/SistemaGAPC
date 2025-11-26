import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
from datetime import date, datetime
import plotly.express as px
import plotly.graph_objects as go

def obtener_datos_cierre_ciclo(id_grupo, fecha_cierre):
    """
    Obtiene todos los datos necesarios para el cierre de ciclo con la nueva lógica
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return None
            
        cursor = conn.cursor(dictionary=True)
        
        # 1. Obtener información básica del grupo
        cursor.execute("""
            SELECT id_grupo, Nombre_grupo, distrito 
            FROM Grupos 
            WHERE id_grupo = %s
        """, (id_grupo,))
        grupo_info = cursor.fetchone()
        
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
            AND MT.fecha BETWEEN '1900-01-01' AND %s
            AND MT.pagada = 1
        """, (id_grupo, fecha_cierre))
        total_multas_grupo = float(cursor.fetchone()['total_multas'])
        
        # 3.2 Total de intereses de préstamos pagados del grupo
        cursor.execute("""
            SELECT COALESCE(SUM(PP.interes), 0) as total_intereses
            FROM prestamo_pagos PP
            JOIN prestamos P ON PP.id_prestamo = P.id_prestamo
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s 
            AND PP.fecha BETWEEN '1900-01-01' AND %s
            AND PP.estado = 'pagado'
        """, (id_grupo, fecha_cierre))
        total_intereses_grupo = float(cursor.fetchone()['total_intereses'])
        
        # 3.3 Total de actividades del grupo
        cursor.execute("""
            SELECT COALESCE(SUM(actividades), 0) as total_actividades
            FROM ahorro_final 
            WHERE id_grupo = %s 
            AND fecha_registro BETWEEN '1900-01-01' AND %s
        """, (id_grupo, fecha_cierre))
        total_actividades_grupo = float(cursor.fetchone()['total_actividades'])
        
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
                AND fecha_registro BETWEEN '1900-01-01' AND %s
            """, (id_grupo, miembro['id_miembro'], fecha_cierre))
            total_ahorros = float(cursor.fetchone()['total_ahorros'])
            
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
            }
        }
        
    except Exception as e:
        st.error(f"Error al obtener datos para cierre de ciclo: {e}")
        return None

def mostrar_resumen_cierre(datos_cierre):
    """
    Muestra un resumen visual del cierre de ciclo con la nueva lógica
    """
    st.markdown("### 📊 Resumen del Cierre de Ciclo")
    
    # KPIs principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "👥 Total Miembros",
            datos_cierre['totales_grupales']['num_miembros'],
            help="Número de miembros en el grupo"
        )
    
    with col2:
        st.metric(
            "💰 Total Ahorros del Grupo",
            f"${datos_cierre['totales_grupales']['total_ahorro_grupo']:,.2f}",
            help="Suma de ahorros individuales de todas las socias"
        )
    
    with col3:
        st.metric(
            "🏦 Fondo Grupal a Repartir",
            f"${datos_cierre['totales_grupales']['fondo_grupal_total']:,.2f}",
            help="Multas + Intereses + Actividades"
        )
    
    # Desglose del fondo grupal
    st.markdown("---")
    st.subheader("🥧 Composición del Fondo Grupal")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💰 Multas",
            f"${datos_cierre['totales_grupales']['total_multas']:,.2f}"
        )
    
    with col2:
        st.metric(
            "💸 Intereses Préstamos",
            f"${datos_cierre['totales_grupales']['total_intereses']:,.2f}"
        )
    
    with col3:
        st.metric(
            "📊 Actividades",
            f"${datos_cierre['totales_grupales']['total_actividades']:,.2f}"
        )
    
    # Gráfico de distribución del fondo grupal
    labels = ['Multas', 'Intereses', 'Actividades']
    values = [
        datos_cierre['totales_grupales']['total_multas'],
        datos_cierre['totales_grupales']['total_intereses'],
        datos_cierre['totales_grupales']['total_actividades']
    ]
    
    fig = px.pie(
        values=values,
        names=labels,
        title='Distribución del Fondo Grupal',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def mostrar_formulario_cierre(datos_cierre):
    """
    Muestra el formulario de cierre de ciclo con la nueva lógica
    """
    st.markdown("---")
    st.markdown("### 📋 Liquidación por Socia")
    st.markdown(f"**Grupo:** {datos_cierre['grupo_info']['Nombre_grupo']} | **Distrito:** {datos_cierre['grupo_info']['distrito']}")
    st.info(f"💡 **Monto por socia del fondo grupal:** ${datos_cierre['totales_grupales']['monto_por_socia']:,.2f}")
    
    # Crear DataFrame para mostrar
    datos_liquidacion = []
    for i, socia in enumerate(datos_cierre['miembros']):
        datos_liquidacion.append({
            'Nº': i + 1,
            'Socia': socia['nombre_completo'],
            'Ahorros Individuales': f"${socia['ahorros_individuales']:,.2f}",
            'Parte Fondo Grupal': f"${socia['monto_fondo_grupal']:,.2f}",
            'Total a Entregar': f"${socia['total_a_entregar']:,.2f}",
            'Entregado': '✅ Sí' if socia.get('entregado', False) else '❌ No'
        })
    
    df = pd.DataFrame(datos_liquidacion)
    st.dataframe(df, use_container_width=True)
    
    # Sección para marcar entregas
    st.markdown("#### ✅ Confirmar Entregas")
    st.warning("Marque cada socia como entregada una vez que reciba su dinero.")
    
    for i, socia in enumerate(datos_cierre['miembros']):
        col_socia1, col_socia2, col_socia3 = st.columns([3, 2, 1])  # Nombres únicos
        
        with col_socia1:
            st.write(f"**{socia['nombre_completo']}**")
            st.write(f"Ahorros: ${socia['ahorros_individuales']:,.2f} + Fondo: ${socia['monto_fondo_grupal']:,.2f}")
            st.write(f"**Total: ${socia['total_a_entregar']:,.2f}**")
        
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
    
    if not datos_cierre or not datos_cierre['miembros']:
        errores.append("No hay miembros en el grupo")
        return errores
    
    # Verificar que todas las socias estén marcadas como entregadas
    socias_pendientes = [socia['nombre_completo'] for socia in datos_cierre['miembros'] if not socia.get('entregado', False)]
    
    if socias_pendientes:
        errores.append(f"Socias pendientes de entrega: {', '.join(socias_pendientes)}")
    
    return errores

def ejecutar_cierre_ciclo(datos_cierre, fecha_cierre, usuario):
    """
    Ejecuta el cierre de ciclo en la base de datos
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return False, "Error de conexión a la base de datos"
            
        cursor = conn.cursor()
        
        # 1. Registrar el cierre de ciclo en la tabla principal
        cursor.execute("""
            INSERT INTO cierre_ciclo 
            (id_grupo, fecha_cierre, total_ahorro, total_fondo, monto_por_socia, usuario_cierre)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            datos_cierre['grupo_info']['id_grupo'],
            fecha_cierre,
            float(datos_cierre['totales_grupales']['total_ahorro_grupo']),
            float(datos_cierre['totales_grupales']['fondo_grupal_total']),
            float(datos_cierre['totales_grupales']['monto_por_socia']),
            usuario
        ))
        
        # Obtener el ID del cierre recién insertado
        id_cierre = cursor.lastrowid
        
        # 2. Registrar detalle por cada socia
        for socia in datos_cierre['miembros']:
            cursor.execute("""
                INSERT INTO cierre_ciclo_detalle 
                (id_cierre, id_miembro, ahorros_individuales, monto_fondo_grupal, 
                 total_entregado, entregado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                id_cierre,
                socia['id_miembro'],
                float(socia['ahorros_individuales']),
                float(socia['monto_fondo_grupal']),
                float(socia['total_a_entregar']),
                1 if socia.get('entregado', False) else 0
            ))
        
        # Confirmar los cambios en la base de datos
        conn.commit()
        conn.close()
        
        return True, f"✅ Cierre de ciclo ejecutado exitosamente. ID: {id_cierre}"
        
    except Exception as e:
        # Si hay error, revertir los cambios
        if conn:
            conn.rollback()
            conn.close()
        return False, f"❌ Error al ejecutar cierre de ciclo: {str(e)}"
def obtener_historial_cierres(id_grupo=None):
    """
    Obtiene el historial de cierres de ciclo
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return None
            
        cursor = conn.cursor(dictionary=True)
        
        if id_grupo:
            # Obtener cierres de un grupo específico
            cursor.execute("""
                SELECT 
                    cc.id_cierre,
                    g.Nombre_grupo,
                    cc.fecha_cierre,
                    cc.total_ahorro,
                    cc.total_fondo,
                    cc.monto_por_socia,
                    cc.usuario_cierre,
                    cc.fecha_registro,
                    COUNT(ccd.id_detalle) as total_socias,
                    SUM(ccd.entregado) as socias_entregadas
                FROM cierre_ciclo cc
                JOIN Grupos g ON cc.id_grupo = g.id_grupo
                LEFT JOIN cierre_ciclo_detalle ccd ON cc.id_cierre = ccd.id_cierre
                WHERE cc.id_grupo = %s
                GROUP BY cc.id_cierre
                ORDER BY cc.fecha_cierre DESC
            """, (id_grupo,))
        else:
            # Obtener todos los cierres
            cursor.execute("""
                SELECT 
                    cc.id_cierre,
                    g.Nombre_grupo,
                    cc.fecha_cierre,
                    cc.total_ahorro,
                    cc.total_fondo,
                    cc.monto_por_socia,
                    cc.usuario_cierre,
                    cc.fecha_registro,
                    COUNT(ccd.id_detalle) as total_socias,
                    SUM(ccd.entregado) as socias_entregadas
                FROM cierre_ciclo cc
                JOIN Grupos g ON cc.id_grupo = g.id_grupo
                LEFT JOIN cierre_ciclo_detalle ccd ON cc.id_cierre = ccd.id_cierre
                GROUP BY cc.id_cierre
                ORDER BY cc.fecha_cierre DESC
            """)
        
        historial = cursor.fetchall()
        conn.close()
        
        return historial
        
    except Exception as e:
        st.error(f"Error al obtener historial de cierres: {e}")
        return None

def mostrar_historial_cierres():
    """
    Muestra el historial de cierres de ciclo
    """
    st.markdown("### 📋 Historial de Cierres de Ciclo")
    
    rol = st.session_state.get("rol", "").lower()
    id_grupo = st.session_state.get("id_grupo")
    
    # Obtener historial según el rol
    if rol == "miembro":
        historial = obtener_historial_cierres(id_grupo)
    else:
        historial = obtener_historial_cierres()
    
    if not historial:
        st.info("No hay cierres de ciclo registrados.")
        return
    
    # Preparar datos para mostrar
    datos_historial = []
    for cierre in historial:
        datos_historial.append({
            'ID': cierre['id_cierre'],
            'Grupo': cierre['Nombre_grupo'],
            'Fecha Cierre': cierre['fecha_cierre'],
            'Total Ahorro': f"${cierre['total_ahorro']:,.2f}",
            'Total Fondo': f"${cierre['total_fondo']:,.2f}",
            'Monto por Socia': f"${cierre['monto_por_socia']:,.2f}",
            'Socias': f"{cierre['socias_entregadas']}/{cierre['total_socias']}",
            'Usuario': cierre['usuario_cierre'],
            'Fecha Registro': cierre['fecha_registro'].strftime('%Y-%m-%d %H:%M')
        })
    
    df = pd.DataFrame(datos_historial)
    st.dataframe(df, use_container_width=True)

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
        fecha_cierre = st.date_input(
            "📅 Fecha de cierre del ciclo",
            date.today(),
            key="cierre_fecha_input"
        )
    
    # ===============================
    # 2. OBTENER Y MOSTRAR DATOS
    # ===============================
    if st.button("🔄 Cargar Datos para Cierre", type="primary", key="btn_cargar_datos"):
        with st.spinner("Cargando datos del ciclo..."):
            datos_cierre = obtener_datos_cierre_ciclo(id_grupo_seleccionado, fecha_cierre)
            
            if datos_cierre:
                # Usar un diccionario temporal en lugar de session_state
                st.session_state.cierre_info = {
                    'datos': datos_cierre,
                    'fecha': fecha_cierre,
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
        
        # Botón para validar y ejecutar cierre
        st.markdown("---")
        st.subheader("✅ Confirmar y Ejecutar Cierre")
        
        col_botones1, col_botones2 = st.columns([1, 1])
        
        with col_botones1:
            if st.button("🔍 Validar Cierre", use_container_width=True, key="btn_validar_cierre"):
                errores = validar_cierre_ciclo(datos_cierre_actualizado)
                if errores:
                    for error in errores:
                        st.error(f"❌ {error}")
                else:
                    st.success("✅ Validación exitosa. Puede proceder con el cierre.")
        
        with col_botones2:
            if st.button("🚀 Ejecutar Cierre de Ciclo", type="primary", use_container_width=True, key="btn_ejecutar_cierre"):
                # Validar antes de ejecutar
                errores = validar_cierre_ciclo(datos_cierre_actualizado)
                if errores:
                    for error in errores:
                        st.error(f"❌ {error}")
                else:
                    with st.spinner("Ejecutando cierre de ciclo..."):
                        exito, mensaje = ejecutar_cierre_ciclo(
                            datos_cierre_actualizado, 
                            st.session_state.cierre_info['fecha'],
                            usuario
                        )
                        
                        if exito:
                            st.success(f"✅ {mensaje}")
                            st.balloons()
                            # Limpiar datos de sesión
                            if 'cierre_info' in st.session_state:
                                del st.session_state.cierre_info
                        else:
                            st.error(f"❌ {mensaje}")
    
    # ===============================
    # 4. BOTÓN REGRESAR
    # ===============================
    st.markdown("---")
    if st.button("⬅️ Regresar al Menú Principal", key="btn_regresar_cierre"):
        st.session_state.page = "menu"
        st.rerun()

# Función auxiliar necesaria (debe estar en tu código)
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
