import streamlit as st
import mysql.connector
from datetime import datetime

def get_db_connection():
    """Establece conexión con la base de datos"""
    try:
        conn = mysql.connector.connect(
            host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
            user="uiazxdhtd3r8o7uv",
            password="uGjZ9MXWemv7vPsjOdA5",
            database="bzn5gsi7ken7lufcglbg",
            port=3306
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Error de conexión a la base de datos: {e}")
        return None

def obtener_miembros_grupo(id_grupo):
    """Obtiene los miembros de un grupo específico usando la tabla Grupomiembros"""
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Usar JOIN con la tabla Grupomiembros (todo junto)
        cursor.execute("""
            SELECT m.id_miembro, m.Nombre 
            FROM Miembros m 
            INNER JOIN Grupomiembros gm ON m.id_miembro = gm.id_miembro 
            WHERE gm.id_grupo = %s
        """, (id_grupo,))
        
        miembros = cursor.fetchall()
        return miembros
        
    except mysql.connector.Error as e:
        st.error(f"Error al obtener miembros: {e}")
        
        # Si hay error, intentar obtener todos los miembros como fallback
        try:
            cursor.execute("SELECT id_miembro, Nombre FROM Miembros")
            miembros = cursor.fetchall()
            st.warning("Usando todos los miembros (fallback por error en relación)")
            return miembros
        except:
            return []
            
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def obtener_registros_ahorro_final(id_grupo):
    """Obtiene los registros de ahorro final de un grupo"""
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT af.*, m.Nombre 
            FROM ahorro_final af 
            JOIN Miembros m ON af.id_miembro = m.id_miembro 
            WHERE af.id_grupo = %s 
            ORDER BY af.fecha_registro DESC
        """, (id_grupo,))
        
        registros = cursor.fetchall()
        return registros
        
    except mysql.connector.Error as e:
        st.error(f"Error al obtener registros: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def obtener_estadisticas_personales(id_miembro, id_grupo):
    """Obtiene estadísticas personales de un miembro específico"""
    conn = get_db_connection()
    if conn is None:
        return {}
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                SUM(ahorros) as total_ahorros,
                SUM(actividades) as total_actividades,
                SUM(retiros) as total_retiros,
                SUM(saldo_final) as total_saldo_final,
                COUNT(*) as total_registros
            FROM ahorro_final 
            WHERE id_miembro = %s AND id_grupo = %s
        """, (id_miembro, id_grupo))
        
        estadisticas = cursor.fetchone()
        
        # Obtener el nombre del miembro
        cursor.execute("SELECT Nombre FROM Miembros WHERE id_miembro = %s", (id_miembro,))
        miembro_info = cursor.fetchone()
        
        if estadisticas and miembro_info:
            estadisticas['nombre'] = miembro_info['Nombre']
            # Convertir None a 0
            for key in ['total_ahorros', 'total_actividades', 'total_retiros', 'total_saldo_final']:
                estadisticas[key] = estadisticas[key] or 0
            
        return estadisticas or {}
        
    except mysql.connector.Error as e:
        st.error(f"Error al obtener estadísticas personales: {e}")
        return {}
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def guardar_registro_ahorro(id_miembro, id_grupo, fecha_registro, ahorros, actividades, retiros):
    """Guarda un nuevo registro de ahorro final"""
    conn = get_db_connection()
    if conn is None:
        return False, "Error de conexión a la base de datos"
    
    try:
        saldo_final = calcular_saldo_final(ahorros, actividades, retiros)
        cursor = conn.cursor()
        
        sql = """INSERT INTO ahorro_final 
                 (id_miembro, id_grupo, fecha_registro, ahorros, actividades, retiros, saldo_final) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(sql, (id_miembro, id_grupo, fecha_registro, ahorros, actividades, retiros, saldo_final))
        conn.commit()
        
        return True, "Registro guardado exitosamente"
        
    except mysql.connector.Error as e:
        return False, f"Error al guardar el registro: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def borrar_registro_ahorro(id_ahorro):
    """Borra un registro de ahorro final"""
    conn = get_db_connection()
    if conn is None:
        return False, "Error de conexión a la base de datos"
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM ahorro_final WHERE id_ahorro = %s", (id_ahorro,))
        conn.commit()
        
        return True, "Registro borrado exitosamente"
        
    except mysql.connector.Error as e:
        return False, f"Error al borrar el registro: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def borrar_multiples_registros(ids_ahorro):
    """Borra múltiples registros de ahorro final"""
    conn = get_db_connection()
    if conn is None:
        return False, "Error de conexión a la base de datos"
    
    try:
        cursor = conn.cursor()
        
        # Crear placeholders para la consulta IN
        placeholders = ', '.join(['%s'] * len(ids_ahorro))
        query = f"DELETE FROM ahorro_final WHERE id_ahorro IN ({placeholders})"
        
        cursor.execute(query, tuple(ids_ahorro))
        conn.commit()
        
        return True, f"{cursor.rowcount} registros borrados exitosamente"
        
    except mysql.connector.Error as e:
        return False, f"Error al borrar los registros: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def calcular_saldo_final(ahorros, actividades, retiros):
    """Calcula el saldo final automáticamente"""
    return ahorros + actividades - retiros

def obtener_nombre_grupo(id_grupo):
    """Obtiene el nombre del grupo desde la base de datos"""
    conn = get_db_connection()
    if conn is None:
        return "Grupo Desconocido"
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nombre_grupo FROM Grupos WHERE id_grupo = %s", (id_grupo,))
        resultado = cursor.fetchone()
        return resultado['nombre_grupo'] if resultado else "Grupo Desconocido"
    except mysql.connector.Error as e:
        st.error(f"Error al obtener nombre del grupo: {e}")
        return "Grupo Desconocido"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def mostrar_ahorro_final(id_grupo):
    """Función principal del módulo Ahorro Final - Versión reorganizada"""
    
    # Obtener nombre del grupo desde la base de datos
    nombre_grupo = obtener_nombre_grupo(id_grupo)
    
    # Título principal con nombre del grupo
    st.markdown(f"""
    <div style='text-align: center;'>
        <h1>💰 Ahorros</h1>
        <h3 style='color: #4C3A60; margin-top: -10px;'>Grupo: {nombre_grupo}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar conexión primero
    conn = get_db_connection()
    if conn is None:
        st.error("No se pudo conectar a la base de datos. Verifica la configuración.")
        return
    else:
        conn.close()
    
    # Obtener datos
    miembros = obtener_miembros_grupo(id_grupo)
    
    if not miembros:
        st.warning("No se encontraron miembros en este grupo.")
        st.info("💡 **Solución:** Asegúrate de que los miembros estén asignados al grupo en el módulo 'Gestión de Miembros'")
        if st.button("👥 Ir a Gestión de Miembros"):
            st.session_state.page = "registrar_miembros"
            st.rerun()
        return
    
    registros = obtener_registros_ahorro_final(id_grupo)
    
    # SECCIÓN 1: REGISTRO DE AHORROS POR PERSONA
    st.subheader("Registrar ahorro")
    with st.form("form_ahorro", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Crear diccionario para mapear id a nombre
            opciones_miembros = {m['id_miembro']: m['Nombre'] for m in miembros}
            miembro_ahorro = st.selectbox(
                "Seleccionar Miembro:",
                options=list(opciones_miembros.keys()),
                format_func=lambda x: opciones_miembros[x],
                key="ahorro_miembro"
            )
        
        with col2:
            fecha_ahorro = st.date_input("Fecha:", value=datetime.now(), key="fecha_ahorro")
        
        with col3:
            monto_ahorro = st.number_input("Monto de Ahorro ($):", min_value=0.0, step=0.01, value=0.0, key="monto_ahorro")
        
        submitted_ahorro = st.form_submit_button("💾 Guardar Ahorro")
        if submitted_ahorro and monto_ahorro > 0:
            success, message = guardar_registro_ahorro(
                miembro_ahorro, id_grupo, fecha_ahorro, 
                monto_ahorro, 0.0, 0.0  # Solo ahorro, actividades=0, retiros=0
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        elif submitted_ahorro:
            st.warning("Por favor ingresa un monto de ahorro mayor a 0")
    
    st.write("---")
    
    # SECCIÓN 2: REGISTRO DE RETIROS POR PERSONA
    st.subheader("💸 Registrar retiro")
    with st.form("form_retiro", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            opciones_miembros = {m['id_miembro']: m['Nombre'] for m in miembros}
            miembro_retiro = st.selectbox(
                "Seleccionar Miembro:",
                options=list(opciones_miembros.keys()),
                format_func=lambda x: opciones_miembros[x],
                key="retiro_miembro"
            )
        
        with col2:
            fecha_retiro = st.date_input("Fecha:", value=datetime.now(), key="fecha_retiro")
        
        with col3:
            monto_retiro = st.number_input("Monto de Retiro ($):", min_value=0.0, step=0.01, value=0.0, key="monto_retiro")
        
        submitted_retiro = st.form_submit_button("💾 Guardar Retiro")
        if submitted_retiro and monto_retiro > 0:
            success, message = guardar_registro_ahorro(
                miembro_retiro, id_grupo, fecha_retiro, 
                0.0, 0.0, monto_retiro  # Solo retiro, ahorros=0, actividades=0
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        elif submitted_retiro:
            st.warning("Por favor ingresa un monto de retiro mayor a 0")
    
    st.write("---")
    
    # SECCIÓN 3: REGISTRO DE ACTIVIDADES (GRUPO COMPLETO)
    st.subheader("🎯 Registrar Actividad del Grupo")
    with st.form("form_actividad", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha_actividad = st.date_input("Fecha:", value=datetime.now(), key="fecha_actividad")
        
        with col2:
            monto_actividad = st.number_input("Monto de Actividad ($):", min_value=0.0, step=0.01, value=0.0, key="monto_actividad")
        
        st.info("💡 **Nota:** Esta actividad representa una entrada de dinero general para el grupo")
        
        submitted_actividad = st.form_submit_button("💾 Guardar Actividad del Grupo")
        if submitted_actividad and monto_actividad > 0:
            # Guardar la actividad como un registro general del grupo (sin miembro específico)
            # Usamos un miembro especial (podría ser el primero o crear un registro especial)
            if miembros:
                miembro_grupo = miembros[0]['id_miembro']  # Usar el primer miembro como representante
                success, message = guardar_registro_ahorro(
                    miembro_grupo, id_grupo, fecha_actividad, 
                    0.0, monto_actividad, 0.0  # Solo actividad, ahorros=0, retiros=0
                )
                if success:
                    st.success(f"✅ Actividad del grupo registrada exitosamente: ${monto_actividad:,.2f}")
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("No hay miembros en el grupo para registrar la actividad")
                
        elif submitted_actividad:
            st.warning("Por favor ingresa un monto de actividad mayor a 0")
    
    # BOTÓN REGRESAR - COMO ESTABA ORIGINALMENTE QUE SÍ FUNCIONABA
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
    st.write("---")
    
    # Mostrar registros existentes en TABLA
    st.subheader("📊 Registros Existentes")
    
    if registros:
        # Preparar datos para la tabla
        datos_tabla = []
        for registro in registros:
            # Mostrar "Actividad Grupal" en lugar del nombre del miembro para actividades grupales
            nombre_mostrar = "Actividad Grupal" if registro['actividades'] > 0 and registro['ahorros'] == 0 and registro['retiros'] == 0 else registro['Nombre']
            
            datos_tabla.append({
                "Fecha": registro['fecha_registro'],
                "Miembro": nombre_mostrar,
                "Ahorros": f"${registro['ahorros']:,.2f}",
                "Actividades": f"${registro['actividades']:,.2f}",
                "Retiros": f"${registro['retiros']:,.2f}",
                "Saldo Final": f"${registro['saldo_final']:,.2f}",
                "ID": registro['id_ahorro']  # Oculto pero necesario para borrar
            })
        
        # Mostrar tabla
        st.dataframe(
            datos_tabla,
            use_container_width=True,
            column_config={
                "Fecha": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
                "Miembro": "Miembro",
                "Ahorros": "Ahorros",
                "Actividades": "Actividades", 
                "Retiros": "Retiros",
                "Saldo Final": st.column_config.TextColumn("Saldo Final"),
                "ID": None  # Ocultar columna ID
            },
            hide_index=True
        )
        
        # SECCIÓN PARA BORRAR REGISTROS - VERSIÓN MEJORADA CON SELECCIÓN MÚLTIPLE
        st.subheader("🗑️ Gestión de Registros")
        
        # Crear opciones para el multiselect
        opciones_borrar = {}
        for r in registros:
            tipo_registro = "Actividad Grupal" if r['actividades'] > 0 and r['ahorros'] == 0 and r['retiros'] == 0 else r['Nombre']
            opciones_borrar[r['id_ahorro']] = f"{tipo_registro} - {r['fecha_registro']} - ${r['saldo_final']:,.2f}"
        
        if opciones_borrar:
            # Multiselect para seleccionar múltiples registros
            registros_seleccionados = st.multiselect(
                "Seleccionar registros para borrar:",
                options=list(opciones_borrar.keys()),
                format_func=lambda x: opciones_borrar[x],
                placeholder="Selecciona uno o más registros..."
            )
            
            # Mostrar información de los registros seleccionados
            if registros_seleccionados:
                st.info(f"📋 **Registros seleccionados para eliminar:** {len(registros_seleccionados)}")
                
                # Mostrar detalles de los registros seleccionados
                with st.expander("Ver detalles de registros seleccionados"):
                    for id_registro in registros_seleccionados:
                        registro = next(r for r in registros if r['id_ahorro'] == id_registro)
                        tipo_registro = "Actividad Grupal" if registro['actividades'] > 0 and registro['ahorros'] == 0 and registro['retiros'] == 0 else registro['Nombre']
                        st.write(f"- **{tipo_registro}** - {registro['fecha_registro']} - Ahorros: ${registro['ahorros']:,.2f} - Actividades: ${registro['actividades']:,.2f} - Retiros: ${registro['retiros']:,.2f}")
            
            # Contenedor para el botón y mensajes de confirmación
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Botón para borrar múltiples registros con confirmación
                if st.button("🗑️ Eliminar Registros Seleccionados", type="secondary", disabled=not registros_seleccionados):
                    if st.session_state.get("confirmar_borrado_multiple", False):
                        success, message = borrar_multiples_registros(registros_seleccionados)
                        if success:
                            st.success(message)
                            st.session_state.confirmar_borrado_multiple = False
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.session_state.confirmar_borrado_multiple = True
                        st.rerun()
            
            with col2:
                # Mostrar mensajes de confirmación en línea horizontal
                if st.session_state.get("confirmar_borrado_multiple", False) and registros_seleccionados:
                    st.error(f"⚠️ **Confirmación requerida:** ¿Estás seguro de borrar {len(registros_seleccionados)} registro(s)? Haz clic nuevamente en 'Eliminar Registros Seleccionados' para confirmar.")
        
        # ESTADÍSTICAS
        st.subheader("📈 Estadísticas")
        
        # Selector para estadísticas (grupo o individual)
        opcion_estadisticas = st.selectbox(
            "Ver estadísticas de:",
            ["Todo el Grupo", "Miembro Específico"]
        )
        
        if opcion_estadisticas == "Todo el Grupo":
            # Estadísticas del grupo completo
            col1, col2, col3, col4 = st.columns(4)
            
            total_ahorros = sum(r['ahorros'] for r in registros)
            total_actividades = sum(r['actividades'] for r in registros)
            total_retiros = sum(r['retiros'] for r in registros)
            saldo_total = sum(r['saldo_final'] for r in registros)
            
            with col1:
                st.metric("Total Ahorros", f"${total_ahorros:,.2f}")
            with col2:
                st.metric("Total Actividades", f"${total_actividades:,.2f}")
            with col3:
                st.metric("Total Retiros", f"${total_retiros:,.2f}")
            with col4:
                st.metric("Saldo Total Grupo", f"${saldo_total:,.2f}")
                
        else:
            # Estadísticas por miembro
            opciones_miembros_estadisticas = {m['id_miembro']: m['Nombre'] for m in miembros}
            miembro_estadisticas = st.selectbox(
                "Seleccionar miembro para estadísticas:",
                options=list(opciones_miembros_estadisticas.keys()),
                format_func=lambda x: opciones_miembros_estadisticas[x],
                key="estadisticas_miembro"
            )
            
            if miembro_estadisticas:
                estadisticas_personales = obtener_estadisticas_personales(miembro_estadisticas, id_grupo)
                
                if estadisticas_personales:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Ahorros", f"${estadisticas_personales['total_ahorros']:,.2f}")
                    with col2:
                        st.metric("Total Actividades", f"${estadisticas_personales['total_actividades']:,.2f}")
                    with col3:
                        st.metric("Total Retiros", f"${estadisticas_personales['total_retiros']:,.2f}")
                    with col4:
                        st.metric("Saldo Final Personal", f"${estadisticas_personales['total_saldo_final']:,.2f}")
                    
                    # Información adicional
                    st.info(f"**Total Registros:** {estadisticas_personales['total_registros']}")
                else:
                    st.info(f"No hay registros para {opciones_miembros_estadisticas[miembro_estadisticas]}")
            
    else:
        st.info("No hay registros de ahorro final para mostrar.")
