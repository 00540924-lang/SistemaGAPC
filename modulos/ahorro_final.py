from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime

ahorro_final_bp = Blueprint('ahorro_final', __name__)

# Configuración de la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bzn5gsi7ken7lufcqlbg"
    )

@ahorro_final_bp.route('/ahorro_final', methods=['GET', 'POST'])
def ahorro_final():
    # Verificar si el administrador está logueado
    if 'id_administrador' not in session:
        return redirect(url_for('login'))
    
    # Verificar si tiene grupo asignado
    if 'id_grupo' not in session:
        return redirect(url_for('seleccionar_grupo'))
    
    id_grupo = session['id_grupo']
    mensaje = None
    error = None
    
    # Procesar el formulario cuando se envía
    if request.method == 'POST':
        try:
            id_miembro = request.form['id_miembro']
            fecha_registro = request.form['fecha_registro']
            saldo_inicial = float(request.form['saldo_inicial'])
            ahorros = float(request.form['ahorros'])
            actividades = float(request.form['actividades'])
            retiros = float(request.form['retiros'])
            saldo_final = saldo_inicial + ahorros + actividades - retiros
            
            # Insertar en la base de datos
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """INSERT INTO ahorro_final 
                     (id_miembro, id_grupo, fecha_registro, saldo_inicial, ahorros, actividades, retiros, saldo_final) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(sql, (id_miembro, id_grupo, fecha_registro, saldo_inicial, ahorros, actividades, retiros, saldo_final))
            conn.commit()
            
            mensaje = "Registro guardado exitosamente"
            cursor.close()
            conn.close()
            
        except Exception as e:
            error = f"Error al guardar el registro: {str(e)}"
    
    # Obtener miembros del mismo grupo
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Obtener miembros del grupo
    cursor.execute("SELECT id_miembro, Nombre FROM miembros WHERE id_grupo = %s", (id_grupo,))
    miembros = cursor.fetchall()
    
    # Obtener registros existentes del grupo
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
    
    return render_template('ahorro_final.html', 
                         miembros=miembros, 
                         registros=registros, 
                         mensaje=mensaje, 
                         error=error,
                         nombre_grupo=session.get('nombre_grupo', ''))

# Función para calcular saldo final (puede ser útil para otras partes del sistema)
def calcular_saldo_final(saldo_inicial, ahorros, actividades, retiros):
    return saldo_inicial + ahorros + actividades - retiros

# Función para obtener registros por miembro
def obtener_ahorros_por_miembro(id_miembro):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM ahorro_final 
        WHERE id_miembro = %s 
        ORDER BY fecha_registro DESC
    """, (id_miembro,))
    
    registros = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return registros

# Función para obtener el saldo total del grupo
def obtener_saldo_total_grupo(id_grupo):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT SUM(saldo_final) as saldo_total 
        FROM ahorro_final 
        WHERE id_grupo = %s
    """, (id_grupo,))
    
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return resultado['saldo_total'] if resultado['saldo_total'] else 0
