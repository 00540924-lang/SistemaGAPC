import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com',
            user='uiazxdhtd3r8o7uv',
            password='uGjZ9MXWemv7vPsjOdA5',
            database='bzn5gsi7ken7lufcglbg',
            port=3306
        )
        if conexion.is_connected():
            print("✅ Conexión establecida")
            return conexion
        else:
            print("❌ Conexión fallida (is_connected = False)")
            return None
    except mysql.connector.Error as e:
        print(f"❌ Error al conectar: {e}")
        return None
