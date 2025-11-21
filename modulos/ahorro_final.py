import streamlit as st
import mysql.connector
from datetime import datetime

def get_db_connection():
    """Establece conexión con la base de datos"""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bzn5gsi7ken7lufcqlbg"
    )

def calcular_saldo_final(saldo_inicial, ahorros, actividades, retiros):
    """Calcula el saldo final automáticamente"""
    return saldo_inicial + ahorros + actividades - retiros

def obtener_miembros_grupo(id_grupo):
    """Obtiene los miembros de un grupo específico"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id_miembro, Nombre FROM miembros WHERE id_grupo = %s", (id_grupo,))
    miembros = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return miembros

def obtener_registros_ahorro_final(id_grupo):
    """Obtiene los registros de ahorro final de un grupo"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT af.*, m.Nombre 
        FROM ahorro_final af 
        JOIN miembros m ON af.id_miembro = m.id_miembro 
        WHERE af.id_grupo = %s 
        ORDER BY af.fecha_registro DESC
    """, (id_grupo,))
    
    registros = cursor.fetchall()
    cursor.close()
    conn.close()
    return registros

def guardar_registro_ahorro(id_miembro, id_grupo, fecha_registro, saldo_inicial, ahorros, actividades, retiros):
    """Guarda un nuevo registro de ahorro final"""
    try:
        saldo_final = calcular_saldo_final(saldo_inicial, ahorros, actividades, retiros)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """INSERT INTO ahorro_final 
                 (id_miembro, id_grupo, fecha_registro, saldo_inicial, ahorros, actividades, retiros, saldo_final) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(sql, (id_miembro, id_grupo, fecha_registro, saldo_inicial, ahorros, actividades, retiros, saldo_final))
        conn.commit()
        
        cursor.close()
        conn.close()
        return True, "Registro guardado exitosamente"
        
    except Exception as e:
        return False, f"Error al guardar el registro: {str(e)}"

def mostrar_ahorro_final(id_grupo):
    """Función principal del módulo Ahorro Final"""
    st.title("💰 Módulo Ahorro Final")
    
    # Obtener datos
    miembros = obtener_miembros_grupo(id_grupo)
    registros = obtener_registros_ahorro_final(id_grupo)
    
    # Formulario para nuevo registro
    with st.form("form_ahorro_final"):
        st.subheader("Nuevo Registro de Ahorro")
        
        col1, col2 = st.columns(2)
        
        with col1:
            id_miembro = st.selectbox(
                "Seleccionar Miembro:",
                options=[m['id_miembro'] for m in miembros],
                format_func=lambda x: next((m['Nombre'] for m in miembros if m['id_miembro'] == x), "")
            )
        
        with col2:
            fecha_registro = st.date_input("Fecha:", value=datetime.now())
        
        st.subheader("Detalles del Ahorro")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            saldo_inicial = st.number_input("Saldo Inicial:", min_value=0.0, step=0.01, value=0.0)
        
        with col2:
            ahorros = st.number_input("Ahorros:", min_value=0.0, step=0.01, value=0.0)
        
        with col3:
            actividades = st.number_input("Actividades:", min_value=0.0, step=0.01, value=0.0)
        
        with col4:
            retiros = st.number_input("Retiros:", min_value=0.0, step=0.01, value=0.0)
        
        # Calcular saldo final automáticamente
        saldo_final = calcular_saldo_final(saldo_inicial, ahorros, actividades, retiros)
        st.info(f"**Saldo Final Calculado: ${saldo_final:,.2f}**")
        
        if st.form_submit_button("💾 Guardar Registro"):
            if id_miembro:
                success, message = guardar_registro_ahorro(
                    id_miembro, id_grupo, fecha_registro, 
                    saldo_inicial, ahorros, actividades, retiros
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Por favor seleccione un miembro")
    
    # Mostrar registros existentes
    st.subheader("📊 Registros Existentes")
    
    if registros:
        # Preparar datos para la tabla
        datos_tabla = []
        for registro in registros:
            datos_tabla.append({
                "Fecha": registro['fecha_registro'],
                "Miembro": registro['Nombre'],
                "Saldo Inicial": f"${registro['saldo_inicial']:,.2f}",
                "Ahorros": f"${registro['ahorros']:,.2f}",
                "Actividades": f"${registro['actividades']:,.2f}",
                "Retiros": f"${registro['retiros']:,.2f}",
                "Saldo Final": f"${registro['saldo_final']:,.2f}"
            })
        
        st.dataframe(datos_tabla, use_container_width=True)
        
        # Estadísticas rápidas
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
