import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
from datetime import date, datetime
import plotly.express as px
import plotly.graph_objects as go

def obtener_datos_cierre_ciclo(id_grupo, fecha_cierre):
    """
    Obtiene todos los datos necesarios para el cierre de ciclo de un grupo
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
            SELECT M.id_miembro, M.nombre, M.apellido
            FROM Miembros M
            JOIN Grupomiembros GM ON M.id_miembro = GM.id_miembro
            WHERE GM.id_grupo = %s AND GM.estado = 'activo'
            ORDER BY M.nombre
        """, (id_grupo,))
        miembros = cursor.fetchall()
        
        # 3. Obtener saldos finales de ahorros por miembro
        datos_cierre = []
        total_ahorro_grupo = 0
        total_fondo_grupo = 0
        
        for miembro in miembros:
            # Saldo final de ahorros individual
            cursor.execute("""
                SELECT COALESCE(SUM(ahorros - retiros), 0) as saldo_ahorros
                FROM ahorro_final 
                WHERE id_grupo = %s AND id_miembro = %s
                AND fecha_registro <= %s
            """, (id_grupo, miembro['id_miembro'], fecha_cierre))
            saldo_ahorro = cursor.fetchone()['saldo_ahorros']
            
            # Aportes al fondo del grupo (actividades)
            cursor.execute("""
                SELECT COALESCE(SUM(actividades), 0) as aporte_fondo
                FROM ahorro_final 
                WHERE id_grupo = %s AND id_miembro = %s
                AND fecha_registro <= %s
            """, (id_grupo, miembro['id_miembro'], fecha_cierre))
            aporte_fondo = cursor.fetchone()['aporte_fondo']
            
            datos_cierre.append({
                'id_miembro': miembro['id_miembro'],
                'nombre_completo': f"{miembro['nombre']} {miembro['apellido']}",
                'saldo_ahorros': float(saldo_ahorro),
                'aporte_fondo': float(aporte_fondo)
            })
            
            total_ahorro_grupo += saldo_ahorro
            total_fondo_grupo += aporte_fondo
        
        # 4. Calcular distribución proporcional del fondo
        if total_fondo_grupo > 0:
            for dato in datos_cierre:
                proporcion = (dato['aporte_fondo'] / total_fondo_grupo) if total_fondo_grupo > 0 else 0
                proporcion_redondeada = round(proporcion, 4)
                
                dato['proporcion_fondo'] = proporcion
                dato['proporcion_redondeada'] = proporcion_redondeada
                dato['retiro'] = 0.0  # Inicializar retiro en 0
                dato['saldo_inicial_siguiente'] = dato['saldo_ahorros']  # Inicialmente igual al saldo final
        
        conn.close()
        
        return {
            'grupo_info': grupo_info,
            'miembros': datos_cierre,
            'totales': {
                'total_ahorro_grupo': float(total_ahorro_grupo),
                'total_fondo_grupo': float(total_fondo_grupo)
            }
        }
        
    except Exception as e:
        st.error(f"Error al obtener datos para cierre de ciclo: {e}")
        return None

def validar_cierre_ciclo(datos_cierre):
    """
    Valida que los datos estén completos para proceder con el cierre
    """
    errores = []
    
    if not datos_cierre or not datos_cierre['miembros']:
        errores.append("No hay miembros activos en el grupo")
        return errores
    
    # Verificar que todos los retiros sean válidos
    total_retiros = 0
    for miembro in datos_cierre['miembros']:
        retiro = miembro.get('retiro', 0)
        saldo_ahorros = miembro.get('saldo_ahorros', 0)
        
        if retiro < 0:
            errores.append(f"Retiro no puede ser negativo para {miembro['nombre_completo']}")
        
        if retiro > saldo_ahorros:
            errores.append(f"Retiro excede el saldo disponible para {miembro['nombre_completo']}")
        
        total_retiros += retiro
    
    # Verificar que la suma de proporciones sea aproximadamente 1
    if datos_cierre['totales']['total_fondo_grupo'] > 0:
        suma_proporciones = sum(miembro.get('proporcion_redondeada', 0) for miembro in datos_cierre['miembros'])
        if abs(suma_proporciones - 1.0) > 0.01:  # Tolerancia del 1%
            errores.append(f"La suma de proporciones ({suma_proporciones}) no es igual a 1")
    
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
        
        # 1. Registrar el cierre de ciclo
        cursor.execute("""
            INSERT INTO cierre_ciclo 
            (id_grupo, fecha_cierre, total_ahorro, total_fondo, usuario_cierre, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (
            datos_cierre['grupo_info']['id_grupo'],
            fecha_cierre,
            datos_cierre['totales']['total_ahorro_grupo'],
            datos_cierre['totales']['total_fondo_grupo'],
            usuario
        ))
        
        id_cierre = cursor.lastrowid
        
        # 2. Registrar detalle por miembro
        for miembro in datos_cierre['miembros']:
            cursor.execute("""
                INSERT INTO cierre_ciclo_detalle 
                (id_cierre, id_miembro, saldo_final_ahorros, proporcion_fondo, 
                 retiro, saldo_inicial_siguiente, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                id_cierre,
                miembro['id_miembro'],
                miembro['saldo_ahorros'],
                miembro.get('proporcion_redondeada', 0),
                miembro.get('retiro', 0),
                miembro.get('saldo_inicial_siguiente', 0)
            ))
            
            # 3. Actualizar saldo de ahorros para el siguiente ciclo
            if miembro.get('retiro', 0) > 0:
                cursor.execute("""
                    INSERT INTO ahorro_final 
                    (id_grupo, id_miembro, fecha_registro, ahorros, retiros, actividades)
                    VALUES (%s, %s, %s, 0, %s, 0)
                """, (
                    datos_cierre['grupo_info']['id_grupo'],
                    miembro['id_miembro'],
                    fecha_cierre,
                    miembro.get('retiro', 0)
                ))
        
        conn.commit()
        conn.close()
        
        return True, "Cierre de ciclo ejecutado exitosamente"
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, f"Error al ejecutar cierre de ciclo: {e}"

def mostrar_resumen_cierre(datos_cierre):
    """
    Muestra un resumen visual del cierre de ciclo
    """
    st.markdown("### 📊 Resumen del Cierre de Ciclo")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "👥 Total Miembros",
            len(datos_cierre['miembros']),
            help="Número de miembros activos en el grupo"
        )
    
    with col2:
        st.metric(
            "💰 Total Ahorro del Grupo",
            f"${datos_cierre['totales']['total_ahorro_grupo']:,.2f}",
            help="Suma total de ahorros de todos los miembros"
        )
    
    with col3:
        st.metric(
            "🏦 Total Fondo del Grupo",
            f"${datos_cierre['totales']['total_fondo_grupo']:,.2f}",
            help="Suma total del fondo grupal"
        )
    
    # Gráfico de distribución del fondo
    if datos_cierre['totales']['total_fondo_grupo'] > 0:
        st.markdown("---")
        st.subheader("🥧 Distribución Proporcional del Fondo")
        
        # Preparar datos para el gráfico
        nombres = [m['nombre_completo'] for m in datos_cierre['miembros']]
        proporciones = [m.get('proporcion_redondeada', 0) * 100 for m in datos_cierre['miembros']]  # En porcentaje
        
        fig = px.pie(
            values=proporciones,
            names=nombres,
            title='Distribución del Fondo Grupal por Miembro (%)',
            hover_data={'Proporción': [f'{p:.2f}%' for p in proporciones]}
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def mostrar_formulario_cierre(datos_cierre):
    """
    Muestra el formulario de cierre de ciclo similar al PDF
    """
    st.markdown("---")
    st.markdown("### 📋 Formulario de Cierre de Ciclo")
    st.markdown(f"**Grupo:** {datos_cierre['grupo_info']['Nombre_grupo']} | **Distrito:** {datos_cierre['grupo_info']['distrito']}")
    
    # Crear DataFrame para edición
    datos_edicion = []
    for i, miembro in enumerate(datos_cierre['miembros']):
        datos_edicion.append({
            'Nº': i + 1,
            'Socia': miembro['nombre_completo'],
            'Saldo Final de Ahorros': miembro['saldo_ahorros'],
            'Aporte al Fondo': miembro.get('aporte_fondo', 0),
            'Proporción del Fondo': f"{miembro.get('proporcion_redondeada', 0) * 100:.2f}%" if miembro.get('proporcion_redondeada') else "0%",
            'Retiro': miembro.get('retiro', 0),
            'Saldo Inicial (Siguiente Ciclo)': miembro.get('saldo_inicial_siguiente', miembro['saldo_ahorros'])
        })
    
    df = pd.DataFrame(datos_edicion)
    
    # Mostrar tabla estática con datos principales
    columnas_estaticas = ['Nº', 'Socia', 'Saldo Final de Ahorros', 'Aporte al Fondo', 'Proporción del Fondo']
    st.dataframe(df[columnas_estaticas], use_container_width=True)
    
    # Sección para editar retiros
    st.markdown("#### 💰 Definir Retiros por Socia")
    
    for i, miembro in enumerate(datos_cierre['miembros']):
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            st.write(f"**{miembro['nombre_completo']}**")
            st.write(f"Saldo disponible: ${miembro['saldo_ahorros']:,.2f}")
        
        with col2:
            retiro = st.number_input(
                f"Monto a retirar",
                min_value=0.0,
                max_value=float(miembro['saldo_ahorros']),
                value=float(miembro.get('retiro', 0)),
                step=10.0,
                key=f"retiro_{i}"
            )
            datos_cierre['miembros'][i]['retiro'] = retiro
        
        with col3:
            saldo_inicial = miembro['saldo_ahorros'] - retiro
            datos_cierre['miembros'][i]['saldo_inicial_siguiente'] = saldo_inicial
            st.metric(
                "Saldo Inicial Siguiente Ciclo",
                f"${saldo_inicial:,.2f}"
            )
    
    return datos_cierre

def vista_cierre_ciclo():
    """
    Módulo de Cierre de Ciclo - Dashboard principal
    """
    # Verificar permisos
    rol = st.session_state.get("rol", "").lower()
    usuario = st.session_state.get("usuario", "")
    id_grupo = st.session_state.get("id_grupo")
    
    if rol not in ["promotor", "institucional"] and usuario != "dark":
        st.error("❌ No tiene permisos para acceder a este módulo.")
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Selección de grupo
        if rol == "institucional" or usuario == "dark":
            grupos = obtener_todos_los_grupos()
            if grupos:
                opciones_grupos = {f"{nombre}": id_grupo for id_grupo, nombre in grupos}
                grupo_seleccionado = st.selectbox(
                    "👥 Seleccione el grupo:",
                    options=list(opciones_grupos.keys())
                )
                id_grupo_seleccionado = opciones_grupos[grupo_seleccionado]
            else:
                st.warning("No se encontraron grupos en el sistema.")
                return
        else:
            # Para promotores, usar su grupo asignado
            id_grupo_seleccionado = id_grupo
            grupo_seleccionado = obtener_nombre_grupo(id_grupo)
            st.info(f"**Grupo asignado:** {grupo_seleccionado}")
    
    with col2:
        fecha_cierre = st.date_input(
            "📅 Fecha de cierre del ciclo",
            date.today(),
            key="fecha_cierre"
        )
    
    # ===============================
    # 2. OBTENER Y MOSTRAR DATOS
    # ===============================
    if st.button("🔄 Cargar Datos para Cierre", type="primary"):
        with st.spinner("Cargando datos del ciclo..."):
            datos_cierre = obtener_datos_cierre_ciclo(id_grupo_seleccionado, fecha_cierre)
            
            if datos_cierre:
                st.session_state.datos_cierre = datos_cierre
                st.session_state.fecha_cierre = fecha_cierre
                st.session_state.id_grupo_cierre = id_grupo_seleccionado
                st.success("✅ Datos cargados exitosamente")
            else:
                st.error("❌ No se pudieron cargar los datos para el cierre")
    
    # ===============================
    # 3. PROCESAR CIERRE SI HAY DATOS
    # ===============================
    if 'datos_cierre' in st.session_state:
        datos_cierre = st.session_state.datos_cierre
        
        # Mostrar resumen
        mostrar_resumen_cierre(datos_cierre)
        
        # Mostrar formulario editable
        datos_cierre_actualizado = mostrar_formulario_cierre(datos_cierre)
        
        # Botón para validar y ejecutar cierre
        st.markdown("---")
        st.subheader("✅ Confirmar y Ejecutar Cierre")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔍 Validar Cierre", use_container_width=True):
                errores = validar_cierre_ciclo(datos_cierre_actualizado)
                if errores:
                    for error in errores:
                        st.error(f"❌ {error}")
                else:
                    st.success("✅ Validación exitosa. Puede proceder con el cierre.")
        
        with col2:
            if st.button("🚀 Ejecutar Cierre de Ciclo", type="primary", use_container_width=True):
                # Validar antes de ejecutar
                errores = validar_cierre_ciclo(datos_cierre_actualizado)
                if errores:
                    for error in errores:
                        st.error(f"❌ {error}")
                else:
                    with st.spinner("Ejecutando cierre de ciclo..."):
                        exito, mensaje = ejecutar_cierre_ciclo(
                            datos_cierre_actualizado, 
                            st.session_state.fecha_cierre,
                            usuario
                        )
                        
                        if exito:
                            st.success(f"✅ {mensaje}")
                            st.balloons()
                            # Limpiar datos de sesión
                            if 'datos_cierre' in st.session_state:
                                del st.session_state.datos_cierre
                        else:
                            st.error(f"❌ {mensaje}")
    
    # ===============================
    # 4. BOTÓN REGRESAR
    # ===============================
    st.markdown("---")
    if st.button("⬅️ Regresar al Menú Principal"):
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
