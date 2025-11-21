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
                SUM(saldo_inicial) as total_saldo_inicial,
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
            for key in ['total_saldo_inicial', 'total_ahorros', 'total_actividades', 'total_retiros', 'total_saldo_final']:
                estadisticas[key] = estadisticas[key] or 0
            
        return estadisticas or {}
        
    except mysql.connector.Error as e:
        st.error(f"Error al obtener estadísticas personales: {e}")
        return {}
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def guardar_registro_ahorro(id_miembro, id_grupo, fecha_registro, saldo_inicial, ahorros, actividades, retiros):
    """Guarda un nuevo registro de ahorro final"""
    conn = get_db_connection()
    if conn is None:
        return False, "Error de conexión a la base de datos"
    
    try:
        saldo_final = calcular_saldo_final(saldo_inicial, ahorros, actividades, retiros)
        cursor = conn.cursor()
        
        sql = """INSERT INTO ahorro_final 
                 (id_miembro, id_grupo, fecha_registro, saldo_inicial, ahorros, actividades, retiros, saldo_final) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(sql, (id_miembro, id_grupo, fecha_registro, saldo_inicial, ahorros, actividades, retiros, saldo_final))
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

def calcular_saldo_final(saldo_inicial, ahorros, actividades, retiros):
    """Calcula el saldo final automáticamente"""
    return saldo_inicial + ahorros + actividades - retiros

def mostrar_ahorro_final(id_grupo):
    """Función principal del módulo Ahorro Final"""
    
    # Obtener nombre del grupo desde la sesión
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo Desconocido")
    
    # Título principal con nombre del grupo
    st.markdown(f"""
    <div style='text-align: center;'>
        <h1>💰 Módulo Ahorro Final</h1>
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
    
    # Formulario para nuevo registro
    with st.form("form_ahorro_final", clear_on_submit=True):
        st.subheader("Nuevo Registro de Ahorro")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Crear diccionario para mapear id a nombre
            opciones_miembros = {m['id_miembro']: m['Nombre'] for m in miembros}
            miembro_seleccionado = st.selectbox(
                "Seleccionar Miembro:",
                options=list(opciones_miembros.keys()),
                format_func=lambda x: opciones_miembros[x]
            )
        
        with col2:
            fecha_registro = st.date_input("Fecha:", value=datetime.now())
        
        st.subheader("Detalles del Ahorro")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            saldo_inicial = st.number_input("Saldo Inicial ($):", min_value=0.0, step=0.01, value=0.0)
        
        with col2:
            ahorros = st.number_input("Ahorros ($):", min_value=0.0, step=0.01, value=0.0)
        
        with col3:
            actividades = st.number_input("Actividades ($):", min_value=0.0, step=0.01, value=0.0)
        
        with col4:
            retiros = st.number_input("Retiros ($):", min_value=0.0, step=0.01, value=0.0)
        
        # Calcular saldo final automáticamente
        saldo_final = calcular_saldo_final(saldo_inicial, ahorros, actividades, retiros)
        st.info(f"**Saldo Final Calculado: ${saldo_final:,.2f}**")
        
        submitted = st.form_submit_button("💾 Guardar Registro")
        if submitted:
            success, message = guardar_registro_ahorro(
                miembro_seleccionado, id_grupo, fecha_registro, 
                saldo_inicial, ahorros, actividades, retiros
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    # BOTÓN REGRESAR - FUERA DEL FORMULARIO
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
    st.write("---")
    
    # Mostrar registros existentes en TABLA
    st.subheader("📊 Registros Existentes")
    
    if registros:
        # Preparar datos para la tabla con botones de borrar
        for i, registro in enumerate(registros):
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 2, 2, 2, 2, 2, 2, 1])
            
            with col1:
                st.write(f"**{registro['fecha_registro']}**")
            with col2:
                st.write(registro['Nombre'])
            with col3:
                st.write(f"${registro['saldo_inicial']:,.2f}")
            with col4:
                st.write(f"${registro['ahorros']:,.2f}")
            with col5:
                st.write(f"${registro['actividades']:,.2f}")
            with col6:
                st.write(f"${registro['retiros']:,.2f}")
            with col7:
                st.write(f"**${registro['saldo_final']:,.2f}**")
            with col8:
                # Botón para borrar registro
                if st.button("🗑️", key=f"borrar_{registro['id_ahorro']}"):
                    # Confirmación antes de borrar
                    if st.session_state.get(f"confirmar_borrar_{registro['id_ahorro']}", False):
                        success, message = borrar_registro_ahorro(registro['id_ahorro'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.session_state[f"confirmar_borrar_{registro['id_ahorro']}"] = True
                        st.warning(f"¿Estás seguro de borrar el registro de {registro['Nombre']} del {registro['fecha_registro']}? Haz clic nuevamente en 🗑️ para confirmar.")
            
            # Mostrar mensaje de confirmación si está pendiente
            if st.session_state.get(f"confirmar_borrar_{registro['id_ahorro']}", False):
                st.info("⚠️ **Confirmación pendiente:** Haz clic nuevamente en 🗑️ para borrar este registro.")
            
            st.write("---")
        
        # ESTADÍSTICAS CON SELECTOR DE MIEMBRO
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
                format_func=lambda x: opciones_miembros_estadisticas[x]
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
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Total Registros:** {estadisticas_personales['total_registros']}")
                    with col2:
                        st.info(f"**Saldo Inicial Acumulado:** ${estadisticas_personales['total_saldo_inicial']:,.2f}")
                else:
                    st.info(f"No hay registros para {opciones_miembros_estadisticas[miembro_estadisticas]}")
            
    else:
        st.info("No hay registros de ahorro final para mostrar.")
