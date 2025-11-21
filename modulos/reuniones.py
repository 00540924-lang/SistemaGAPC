import streamlit as st
from datetime import datetime, time
import mysql.connector
from modulos.config.conexion import obtener_conexion
import pandas as pd

def mostrar_reuniones(id_grupo):
    """
    Módulo de Reuniones.
    Solo accesible por usuarios con rol 'miembro' o institucional.
    """
    
    # ===============================
    # 0. Verificar acceso
    # ===============================
    rol = st.session_state.get("rol", "").lower()
    usuario = st.session_state.get("usuario", "").lower()

    if rol not in ["miembro", "institucional"] and usuario != "dark":
        st.error("❌ No tiene permisos para acceder a este módulo.")
        return

    if rol == "miembro" and not id_grupo:
        st.error("❌ No tiene un grupo asignado. Contacte al administrador.")
        return

    st.title("📋 Registro de Reuniones del Grupo")

    # ===============================
    # 1. Conexión BD
    # ===============================
    conn = obtener_conexion()
    if not conn:
        st.error("❌ Error al conectar a la base de datos.")
        return
    cursor = conn.cursor(dictionary=True)

    # ===============================
    # 2. Datos de la reunión
    # ===============================
    st.subheader("🗂 Información general")
    fecha = st.date_input("📅 Fecha de la reunión", datetime.now().date())
    hora = st.time_input("⏰ Hora de inicio", datetime.now().time())

    # ===============================
    # 3. Agenda de la reunión (Desde tu documento)
    # ===============================
    st.write("---")
    st.subheader("📝 Agenda de actividades")

    agenda_default = """
**EMPEZAR LA REUNIÓN**
- La presidenta abre formalmente la reunión.
- La secretaria registra asistencia y multas.
- La secretaria lee las reglas internas.

**DINERO QUE ENTRA**
- La tesorera cuenta el dinero de la caja.
- Las socias depositan ahorros.
- Las socias depositan dinero de otras actividades.
- La secretaria calcula el total de dinero que entra.
- La tesorera verifica el monto total.

**DINERO QUE SALE**
- Las socias solicitan y evalúan préstamos.
- La tesorera desembolsa préstamos aprobados.
- La secretaria registra desembolsos e intereses.
- La secretaria calcula total de dinero que sale.
- La tesorera verifica el dinero y anuncia el saldo.
- La presidenta cierra la caja y entrega llaves.

**CERRAR LA REUNIÓN**
- La presidenta pregunta si hay asuntos pendientes.
- La presidenta cierra formalmente la reunión.
"""

    agenda = st.text_area("Agenda de la reunión", agenda_default, height=300)

    # ===============================
    # 4. Observaciones
    # ===============================
    st.write("---")
    st.subheader("🗒 Observaciones")
    observaciones = st.text_area("Escriba aquí las observaciones de la reunión", height=150)

    # ===============================
    # 5. Guardar datos en BD
    # ===============================
    if st.button("💾 Guardar reunión"):
        
        cursor.execute("""
            INSERT INTO Reuniones (id_grupo, fecha, hora, agenda, observaciones)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_grupo, fecha, hora, agenda, observaciones))

        conn.commit()
        st.success("✅ Reunión guardada con éxito.")

    # ===============================
    # 6. Historial de reuniones
    # ===============================
    st.write("---")
    st.subheader("📚 Historial de reuniones")

    cursor.execute("""
        SELECT * FROM Reuniones
        WHERE id_grupo = %s
        ORDER BY fecha DESC, hora DESC
    """, (id_grupo,))
    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros)
        st.dataframe(df)
    else:
        st.info("No hay reuniones registradas.")

    # ===============================
    # 7. Regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    cursor.close()
    conn.close()
