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
        <h1>💰 Gestión de ahorro</h1>
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
            # Necesitarías definir cómo manejar la navegación entre páginas
            st.error("La navegación entre páginas no está configurada")
        return
    
    registros = obtener_registros_ahorro_final(id_grupo)
    
    # SECCIÓN 1: REGISTRO DE AHORROS POR PERSONA
    st.subheader("💰 Registrar Ahorro por Persona")
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
    st.subheader("💸 Registrar Retiro por Persona")
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
        
        st.info("💡 **Nota:** Las actividades se aplican a TODOS los miembros del grupo por igual")
        
        submitted_actividad = st.form_submit_button("💾 Guardar Actividad para Todos")
        if submitted_actividad and monto_actividad > 0:
            # Guardar la actividad para cada miembro del grupo
            success_count = 0
            error_messages = []
            
            for miembro in miembros:
                success, message = guardar_registro_ahorro(
                    miembro['id_miembro'], id_grupo, fecha_actividad, 
                    0.0, monto_actividad, 0.0  # Solo actividad, ahorros=0, retiros=0
                )
                if success:
                    success_count += 1
                else:
                    error_messages.append(f"{miembro['Nombre']}: {message}")
            
            if success_count == len(miembros):
                st.success(f"✅ Actividad registrada exitosamente para todos los {success_count} miembros")
            elif success_count > 0:
                st.warning(f"⚠️ Actividad registrada para {success_count} de {len(miembros)} miembros")
                for error in error_messages:
                    st.error(error)
            else:
                st.error("❌ No se pudo registrar la actividad para ningún miembro")
                for error in error_messages:
                    st.error(error)
            
            if success_count > 0:
                st.rerun()
                
        elif submitted_actividad:
            st.warning("Por favor ingresa un monto de actividad mayor a 0")
    
    # BOTÓN REGRESAR
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        # Necesitarías definir cómo manejar la navegación entre páginas
        st.error("La navegación entre páginas no está configurada")
    st.write("---")
    
    # Mostrar registros existentes en TABLA (se mantiene igual)
    st.subheader("📊 Registros Existentes")
    
    if registros:
        # Preparar datos para la tabla
        datos_tabla = []
        for registro in registros:
            datos_tabla.append({
                "Fecha": registro['fecha_registro'],
                "Miembro": registro['Nombre'],
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
        
        # SECCIÓN PARA BORRAR REGISTROS (se mantiene igual)
        st.subheader("🗑️ Gestión de Registros")
        
        # Selector para elegir qué registro borrar
        opciones_borrar = {r['id_ahorro']: f"{r['Nombre']} - {r['fecha_registro']} - ${r['saldo_final']:,.2f}" for r in registros}
        
        if opciones_borrar:
            registro_a_borrar = st.selectbox(
                "Seleccionar registro para borrar:",
                options=list(opciones_borrar.keys()),
                format_func=lambda x: opciones_borrar[x]
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                # Botón para borrar con confirmación
                if st.button("Borrar Registro", type="secondary"):
                    if st.session_state.get("confirmar_borrado", False):
                        success, message = borrar_registro_ahorro(registro_a_borrar)
                        if success:
                            st.success(message)
                            st.session_state.confirmar_borrado = False
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.session_state.confirmar_borrado = True
                        st.warning("⚠️ ¿Estás seguro de borrar este registro? Haz clic nuevamente en 'Borrar Registro' para confirmar.")
            
            with col2:
                if st.session_state.get("confirmar_borrado", False):
                    st.error("**Confirmación pendiente:** Haz clic nuevamente en 'Borrar Registro' para confirmar la eliminación.")
        
        # ESTADÍSTICAS (se mantiene igual)
        st.subheader("📈 Estadísticas")
        
        # Selector para estadísticas (grupo o individual)
        opcion_estadisticas = st.selectbox(
            "Ver estadísticas de:",
            ["Todo el Grupo", "Miembro Específico"]
        )
        
        if opcion_estadisticas == "Todo el Grupo":
            # Estadísticas del grupo completo
            col1, col2, col3 = st.columns(3)
            
            total_ahorros = sum(r['ahorros'] for r in registros)
            total_retiros = sum(r['retiros'] for r in registros)
            saldo_total = sum(r['saldo_final'] for r in registros)
            
            with col1:
                st.metric("Total Ahorros", f"${total_ahorros:,.2f}")
            with col2:
                st.metric("Total Retiros", f"${total_retiros:,.2f}")
            with col3:
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
