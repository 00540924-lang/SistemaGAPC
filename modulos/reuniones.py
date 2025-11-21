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
        # Agenda de la reunión (mejor visual)
        # -----------------------
        st.markdown("<hr style='border:1px solid #D1C4E9;'>", unsafe_allow_html=True)
        st.subheader("📝 Agenda de actividades")

        st.markdown(
            """
            <div style='background-color:#EDE7F6; padding:15px; border-radius:12px; 
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <h4 style='color:#6A1B9A;'>✅ EMPEZAR LA REUNIÓN</h4>
                <ul style='margin-left:20px;'>
                    <li>La presidenta abre formalmente la reunión.</li>
                    <li>La secretaria registra asistencia y multas.</li>
                    <li>La secretaria lee las reglas internas.</li>
                </ul>

                <h4 style='color:#2E7D32;'>💰 DINERO QUE ENTRA</h4>
                <ul style='margin-left:20px;'>
                    <li>La tesorera cuenta el dinero de la caja.</li>
                    <li>Las socias depositan ahorros.</li>
                    <li>Las socias depositan dinero de otras actividades.</li>
                    <li>La secretaria calcula el total de dinero que entra.</li>
                    <li>La tesorera verifica el monto total.</li>
                </ul>

                <h4 style='color:#C62828;'>💸 DINERO QUE SALE</h4>
                <ul style='margin-left:20px;'>
                    <li>Las socias solicitan y evalúan préstamos.</li>
                    <li>La tesorera desembolsa préstamos aprobados.</li>
                    <li>La secretaria registra desembolsos e intereses.</li>
                    <li>La secretaria calcula total de dinero que sale.</li>
                    <li>La tesorera verifica el dinero y anuncia el saldo.</li>
                    <li>La presidenta cierra la caja y entrega llaves.</li>
                </ul>

                <h4 style='color:#6A1B9A;'>📌 CERRAR LA REUNIÓN</h4>
                <ul style='margin-left:20px;'>
                    <li>La presidenta pregunta si hay asuntos pendientes.</li>
                    <li>La presidenta cierra formalmente la reunión.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Permitir edición opcional
        agenda_edicion = st.text_area("✏️ Editar agenda de la reunión (opcional)", height=200)

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
            """, (id_grupo, fecha, hora, agenda_edicion if agenda_edicion else agenda_default, observaciones))
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
