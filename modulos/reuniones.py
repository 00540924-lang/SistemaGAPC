import streamlit as st
from datetime import datetime
import mysql.connector
from modulos.config.conexion import obtener_conexion
import pandas as pd

def mostrar_reuniones(id_grupo):
    """
    Módulo de Reuniones.
    Solo accesible por usuarios con rol 'miembro'.
    """

    rol = st.session_state.get("rol", "").lower()
    usuario = st.session_state.get("usuario", "").lower()

    if rol != "miembro":
        st.error("❌ Solo los miembros pueden acceder a este módulo.")
        return

    if not id_grupo:
        st.error("❌ No se encontró el grupo del usuario. Contacte al administrador.")
        return

    # ===============================
    # Nombre del grupo
    # ===============================
    nombre_grupo = st.session_state.get("nombre_grupo", "Sin Grupo")

    # ===============================
    # Título dinámico
    # ===============================
    st.markdown(
        f"<h1 style='text-align:center; color:#4C3A60;'>📋 Registro de Reuniones – {nombre_grupo}</h1>",
        unsafe_allow_html=True
    )

    # ===============================
    # Conexión BD
    # ===============================
    conn = obtener_conexion()
    if not conn:
        st.error("❌ Error al conectar a la base de datos.")
        return
    cursor = conn.cursor(dictionary=True)

    # ===============================
    # Contenedor principal
    # ===============================
    with st.container():
        st.markdown(
            """
            <div style='background-color:#F7F3FA; padding:20px; border-radius:12px; 
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
            """,
            unsafe_allow_html=True
        )

        # -----------------------
        # Información general
        # -----------------------
        st.subheader("🗂 Información de la reunión")
        fecha = st.date_input("📅 Fecha de la reunión", datetime.now().date())
        hora = st.time_input("⏰ Hora de inicio", datetime.now().time())

        # -----------------------
        # Agenda de la reunión
        # -----------------------
        st.markdown("<hr style='border:1px solid #D1C4E9;'>", unsafe_allow_html=True)
        st.subheader("📝 Agenda de actividades")

        # Contenedor estilizado para la agenda
        st.markdown(
            """
            <div style='background-color:#EFEAF6; padding:15px; border-radius:12px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.08);'>
            """,
            unsafe_allow_html=True
        )

        # Dividir la agenda en dos columnas para mejor legibilidad
        col1, col2 = st.columns(2)

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

        # Dividir contenido de agenda en dos partes
        lineas = agenda_default.strip().split("\n")
        mitad = len(lineas) // 2

        with col1:
            st.text_area("Parte 1 de la Agenda", "\n".join(lineas[:mitad]), height=250)

        with col2:
            st.text_area("Parte 2 de la Agenda", "\n".join(lineas[mitad:]), height=250)

        st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------
        # Observaciones
        # -----------------------
        st.markdown("<hr style='border:1px solid #D1C4E9;'>", unsafe_allow_html=True)
        st.subheader("🗒 Observaciones")
        observaciones = st.text_area("Escriba aquí las observaciones de la reunión", height=150)

        # -----------------------
        # Guardar reunión
        # -----------------------
        st.markdown("<hr style='border:1px solid #D1C4E9;'>", unsafe_allow_html=True)
        if st.button("💾 Guardar reunión", help="Guarda la reunión en la base de datos"):
            cursor.execute("""
                INSERT INTO Reuniones (id_grupo, fecha, hora, agenda, observaciones)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_grupo, fecha, hora, agenda_default, observaciones))
            conn.commit()
            st.success("✅ Reunión guardada con éxito.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ===============================
    # Historial de reuniones
    # ===============================
    st.markdown("<br><h2 style='color:#4C3A60;'>📚 Historial de reuniones</h2>", unsafe_allow_html=True)
    cursor.execute("""
        SELECT fecha, hora, agenda, observaciones FROM Reuniones
        WHERE id_grupo = %s
        ORDER BY fecha DESC, hora DESC
    """, (id_grupo,))
    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay reuniones registradas.")

    # ===============================
    # Botón regresar
    # ===============================
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    cursor.close()
    conn.close()

