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
    """Obtiene los miembros de un grupo específico"""
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Intentamos con diferentes nombres de columna comunes
        consultas = [
            "SELECT id_miembro, Nombre FROM Miembros WHERE id_grupo = %s",
            "SELECT id_miembro, Nombre FROM Miembros WHERE grupo_id = %s",
            "SELECT id_miembro, Nombre FROM Miembros WHERE IdGrupo = %s",
            "SELECT id_miembro, Nombre FROM Miembros WHERE idGrupo = %s",
            "SELECT id_miembro, Nombre FROM Miembros"  # Si no hay filtro por grupo
        ]
        
        miembros = []
        for consulta in consultas:
            try:
                if "WHERE" in consulta:
                    cursor.execute(consulta, (id_grupo,))
                else:
                    cursor.execute(consulta)
                miembros = cursor.fetchall()
                if miembros:
                    break
            except mysql.connector.Error:
                continue
        
        # Si no encontramos miembros con filtro, mostramos todos
        if not miembros:
            cursor.execute("SELECT id_miembro, Nombre FROM Miembros")
            miembros = cursor.fetchall()
            
        return miembros
        
    except mysql.connector.Error as e:
        st.error(f"Error al obtener miembros: {e}")
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
        
        # Intentar diferentes formas de join
        consultas = [
            """
            SELECT af.*, m.Nombre 
            FROM ahorro_final af 
            JOIN Miembros m ON af.id_miembro = m.id_miembro 
            WHERE af.id_grupo = %s 
            ORDER BY af.fecha_registro DESC
            """,
            """
            SELECT af.*, m.Nombre 
            FROM ahorro_final af 
            JOIN Miembros m ON af.id_miembro = m.id_miembro 
            ORDER BY af.fecha_registro DESC
            """
        ]
        
        registros = []
        for consulta in consultas:
            try:
                if "WHERE" in consulta:
                    cursor.execute(consulta, (id_grupo,))
                else:
                    cursor.execute(consulta)
                registros = cursor.fetchall()
                if registros:
                    break
            except mysql.connector.Error:
                continue
        
        return registros
        
    except mysql.connector.Error as e:
        st.error(f"Error al obtener registros: {e}")
        return []
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
        st.warning("No se encontraron miembros en la base de datos.")
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
    
    # Mostrar registros existentes
    st.subheader("📊 Registros Existentes")
    
    if registros:
        # Mostrar datos en formato tabla
        for i, registro in enumerate(registros):
            with st.expander(f"{registro['Nombre']} - {registro['fecha_registro']}"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Saldo Inicial", f"${registro['saldo_inicial']:,.2f}")
                with col2:
                    st.metric("Ahorros", f"${registro['ahorros']:,.2f}")
                with col3:
                    st.metric("Actividades", f"${registro['actividades']:,.2f}")
                with col4:
                    st.metric("Retiros", f"${registro['retiros']:,.2f}")
                
                st.metric("**Saldo Final**", f"${registro['saldo_final']:,.2f}", 
                         delta=f"${registro['saldo_final'] - registro['saldo_inicial']:,.2f}")
        
        # Estadísticas rápidas
        st.subheader("📈 Estadísticas del Grupo")
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
        st.info("No hay registros de ahorro final para mostrar.")
